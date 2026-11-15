from src.devagent.config import close_settings as settings

def test_config():
    print("配置读取成功！")
    print(f"接口地址：{settings.llm_base_url}")
    print(f"模型名称：{settings.llm_model}")
    # 密钥只打印前几位，避免泄露
    print(f"API密钥前5位：{settings.llm_api_key[:5]}...")

if __name__ == "__main__":
    test_config()
