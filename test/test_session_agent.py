from src.devagent.agent.tool_agent import tool_agent


def test_multi_turn():
    session_id = "test_session_001"

    print("=== 第一轮提问 ===")
    answer1 = tool_agent.run_with_session(
        session_id,
        "项目里的配置文件是哪个？",
    )
    print(answer1)
    print("\n" + "=" * 50 + "\n")

    print("=== 第二轮提问（承接上文，不重复说配置文件） ===")
    answer2 = tool_agent.run_with_session(
        session_id,
        "它里面定义了哪几个变量？",
    )
    print(answer2)


if __name__ == "__main__":
    test_multi_turn()
