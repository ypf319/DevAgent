from typing import TypedDict
from langgraph.graph import StateGraph, END

class State(TypedDict):
    content: str
    count: int  # 记录循环次数

def think_node(state: State) -> dict:
    """思考节点：判断要不要继续循环"""
    print(f"第 {state['count']} 次思考")
    return {"count": state["count"] + 1}

def process_node(state: State) -> dict:
    """处理节点：模拟调用工具/检索RAG"""
    return {"content": state["content"] + " → 处理了一次"}

def should_continue(state: State) -> str:
    """条件边函数：返回下一个节点的名字"""
    if state["count"] < 3:
        return "process"  # 还没到3次，继续去处理
    else:
        return END        # 够3次了，结束

# 建图
builder = StateGraph(State)
builder.add_node("think", think_node)
builder.add_node("process", process_node)

builder.set_entry_point("think")

# 加条件边：think 干完，走 should_continue 判断
builder.add_conditional_edges(
    "think",
    should_continue,
    # 映射：返回值 → 对应节点
    {
        "process": "process",
        END: END
    }
)

# process 干完 → 回到 think（形成循环）
builder.add_edge("process", "think")

app = builder.compile()

result = app.invoke({"content": "初始内容", "count": 0})
print(result["content"])
