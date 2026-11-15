from src.devagent.llm_client import LLMClient

def test_llm_client(content:str):
    print("loading...")
    messages = [
        {"role": "user", "content": content},
    ]
    res = LLMClient().chat(messages)

    ans = res["choices"][0]["message"]
    print(ans)

if __name__ == '__main__':
    test_llm_client("用一句话解释什么是api调用")
