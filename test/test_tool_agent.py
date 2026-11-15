from src.devagent.agent.tool_agent import tool_agent

def test_simple_question():
    print("=== 测试1：不需要工具的简单问题 ===")
    answer = tool_agent.run("1+1等于几？")
    print("回答：", answer)
    print()

def test_file_question():
    print("=== 测试2：需要读文件的问题 ===")
    answer = tool_agent.run("src/devagent/config.py 这个文件里定义了什么？")
    print("回答：", answer)

if __name__ == "__main__":
    test_simple_question()
    print("="*50)
    test_file_question()
