from src.devagent.tools.tool_registry import TOOLS_DEFINITION, TOOL_FUNCTIONS


def test_tool_registry():
    print("已注册的工具列表：")
    for tool in TOOLS_DEFINITION:
        func = tool["function"]
        print(f"- 工具名：{func['name']}")
        print(f"  功能说明：{func['description']}")
        print(f"  必填参数：{func['parameters']['required']}")

    print("\n" + "-" * 40)
    print("测试通过工具名调用函数：")

    # 通过工具名拿到实际函数
    read_file_func = TOOL_FUNCTIONS["read_file"]
    # 执行函数读取文件
    content = read_file_func("src/devagent/config.py")
    print(f"执行成功，读取到文件前50字符：{content[:50]}...")


if __name__ == "__main__":
    test_tool_registry()
