import json
from typing import TypedDict, Any

from langgraph.graph import StateGraph, END

from .session import session_manager
from ..llm_client import llm_client
from ..exceptions import ToolCallError
from ..tools.tool_registry import TOOLS_DEFINITION, TOOL_FUNCTIONS


# 用 TypedDict 定义共享状态
class AgentState(TypedDict):
    messages: list[dict[str, Any]]
    current_turn: int
    max_turns: int


def model_node(state: AgentState) -> dict:
    messages = state["messages"]

    # 把工具定义传给大模型，让它决定要不要调用工具
    response = llm_client.chat(messages, TOOLS_DEFINITION)
    assistant_msg = response["choices"][0]["message"]
    messages.append(assistant_msg)

    return {
        "messages": messages,
        "current_turn": state["current_turn"] + 1,
    }


def tool_node(state: AgentState) -> dict:
    messages = list(state["messages"])
    assistant_msg = messages[-1]
    tool_calls = assistant_msg.get("tool_calls") or []

    for tool_call in tool_calls:
        tool_name = tool_call["function"]["name"]
        tool_arg_str = tool_call["function"]["arguments"]
        tool_id = tool_call["id"]

        if tool_name not in TOOL_FUNCTIONS:
            raise ToolCallError(f"未知工具：{tool_name}")

        try:
            tool_args = json.loads(tool_arg_str)
        except Exception as e:
            raise ToolCallError(f"工具参数解析失败：{e}") from e

        print(f"[Agent] 正在调用工具：{tool_name}，参数：{tool_args}")

        try:
            func = TOOL_FUNCTIONS[tool_name]
            result = func(**tool_args)
        except Exception as e:
            result = f"工具执行出错：{str(e)}"

        messages.append({
                "role": "tool",
                "tool_call_id": tool_id,
                "content": str(result)
            })

    return {"messages": messages}


def router(state: AgentState) -> str:
    if state["current_turn"] >= state["max_turns"]:
        return "end"

    messages = state["messages"]
    assistant_msg = messages[-1]

    if assistant_msg.get("tool_calls"):
        return "tool"

    return "end"


def build_agent_graph():
    workflow = StateGraph(AgentState)

    workflow.add_node("model", model_node)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("model")

    workflow.add_conditional_edges(
        source="model",
        path=router,
        path_map={
            "tool": "tools",
            "end": END,
        },
    )

    workflow.add_edge("tools", "model")

    app = workflow.compile()
    return app


class GraphAgent:
    def __init__(self):
        self.app = build_agent_graph()
        self.max_turns = 5
        self.system_prompt = """
你是一个专业的代码仓库助手，你可以调用工具来查找和读取代码，基于真实内容回答用户问题。

【可用工具】
1. search_codebase：全局语义搜索代码库，不知道具体文件名时优先用它
2. read_file：读取指定文件的完整内容，知道具体文件名、需要看完整代码时用它

【使用流程建议】
- 第一步：先用 search_codebase 搜索相关代码片段
- 第二步：如果片段信息不够，再用 read_file 读取对应完整文件
- 第三步：基于获取到的信息给出最终答案

【核心规则】
1. 绝对不编造代码、不编造文件内容，所有结论必须来自工具返回的结果
2. 回答必须严格按照固定格式输出

【输出格式】
### 回答
（在这里写清晰、准确的答案，分点说明）

### 信息来源
- 文件路径1：相关说明
- 文件路径2：相关说明
        """.strip()

    def run_with_session(self, query: str, session_id:str) -> str:
        messages = session_manager.load_session(session_id, self.system_prompt)
        messages.append({
            "role": "user",
            "content": query,
        })
        initial_state: AgentState = {
            "messages": messages,
            "current_turn": 0,
            "max_turns": self.max_turns,
        }

        result = self.app.invoke(initial_state)
        session_manager.save_session(session_id, result["messages"])

        return result["messages"][-1]["content"]

    def run(self, user_query: str) -> str:
        """
        运行智能体，接口和之前的 ToolAgent.run 完全一样
        """
        # 初始化状态
        initial_state = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_query}
            ],
            "max_turns": self.max_turns,
            "current_turn": 0
        }

        # 运行整个工作流
        result = self.app.invoke(initial_state)

        # 取出最后一条消息，就是最终回答
        return result["messages"][-1]["content"]


graph_agent = GraphAgent()
