import json
from ..llm_client import llm_client
from ..tools.tool_registry import TOOLS_DEFINITION,TOOL_FUNCTIONS
from ..exceptions import ToolCallError
from .session import session_manager

class ToolAgent:
    def __init__(self):
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

    def run(self, user_query:str) -> str:
        messages = [
            {"role":"system", "content":self.system_prompt },
            {"role":"user", "content":user_query },
        ]



        max_try = 5
        for _ in range(max_try):
            response = llm_client.chat(messages,TOOLS_DEFINITION)
            assistant_msg = response["choices"][0]["message"]
            messages.append(assistant_msg)

            if "tool_calls" in assistant_msg and assistant_msg["tool_calls"] is not None:
                tool_calls = assistant_msg["tool_calls"]

                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args_str = tool_call["function"]["arguments"]
                    tool_call_id = tool_call["id"]

                    try:
                        tool_args = json.loads(tool_args_str)
                    except json.JSONDecodeError as e:
                        raise ToolCallError(f"工具参数解析失败：{e}") from e

                    if tool_name not in TOOL_FUNCTIONS:
                        raise ToolCallError(f"未知工具：{tool_name}")

                    print(f"[Agent] 正在调用工具：{tool_name}，参数：{tool_args}")
                    try:
                        tool_result = TOOL_FUNCTIONS[tool_name](**tool_args)
                    except Exception as e:
                        tool_result = f"工具执行出错：{str(e)}"

                    messages.append({
                        "role":"tool",
                        "tool_call_id":tool_call_id,
                        "content":tool_result
                    })
                continue
            else:
                return assistant_msg["content"]
        return "已达到最大思考轮次，未能完成回答。"




    def run_with_session(self, session_id:str, user_query:str) -> str:

        messages = session_manager.load_session(session_id,self.system_prompt)

        messages.append({
            "role":"user",
            "content":user_query,
        })
        max_try = 5
        for _ in range(max_try):
            assistant_msg = llm_client.chat(messages, TOOLS_DEFINITION)["choices"][0]["message"]
            messages.append(assistant_msg)

            if "tool_calls" in assistant_msg and assistant_msg["tool_calls"] is not None:
                tool_calls = assistant_msg["tool_calls"]

                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    tool_args_str = tool_call["function"]["arguments"]
                    tool_call_id = tool_call["id"]

                    try:
                        tool_args = json.loads(tool_args_str)
                    except json.JSONDecodeError as e:
                        raise ToolCallError(f"工具参数解析失败：{e}") from e

                    if tool_name not in TOOL_FUNCTIONS:
                        raise ToolCallError(f"未知工具：{tool_name}")

                    print(f"[Agent] 正在调用工具：{tool_name}，参数：{tool_args}")
                    try:
                        tool_result = TOOL_FUNCTIONS[tool_name](**tool_args)
                    except Exception as e:
                        tool_result = f"工具执行出错：{str(e)}"

                    messages.append({
                        "role":"tool",
                        "tool_call_id":tool_call_id,
                        "content":tool_result
                    })
                continue

            else:
                session_manager.save_session(session_id,messages)
                return assistant_msg["content"]

        session_manager.save_session(session_id, messages)
        return "已达到最大思考轮次，未能完成回答。"


tool_agent = ToolAgent()







