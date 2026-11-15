from src.devagent.agent.tool_agent import tool_agent

def test_rag_search():
    print("=== 测试RAG检索问答（不指定文件名） ===")
    # 不告诉它文件名，直接问问题，看它会不会自动搜索
    answer = tool_agent.run("项目里的配置是怎么管理的？用了什么库？")
    print(answer)

if __name__ == "__main__":
    test_rag_search()