import argparse
from .agent.tool_agent import tool_agent

def main():
    parser = argparse.ArgumentParser(
        description="DevAgent - 你的代码仓库智能助手"
    )

    parser.add_argument(
        "query",
        help="你想问的问题，比如 'src/devagent/config.py 是干嘛的"
    )

    args = parser.parse_args()

    # 打印欢迎信息
    print("=" * 50)
    print("🤖 DevAgent 代码智能助手")
    print("=" * 50)
    print(f"你的问题：{args.query}")
    print("-" * 50)

    # 调用智能体执行
    try:
        answer = tool_agent.run(args.query)
        print("\n" + answer)
    except Exception as e:
        print(f"\n❌ 执行出错：{str(e)}")


if __name__ == "__main__":
    main()