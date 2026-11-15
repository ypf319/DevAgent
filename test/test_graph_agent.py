from src.devagent.agent.graph_agent import graph_agent


def test_graph_agent(session_id: str = "主对话"):
    print("=== 测试 LangGraph 版智能体 ===")
    answer = graph_agent.run("这个项目最终交付的运行结构大概是什么样子？",session_id)
    print(answer)

if __name__ == "__main__":
    test_graph_agent()

