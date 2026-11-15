"""step7 实战：并发调用 LLM 接口

这是唯一需要联网的一步，会真实消耗少量 token。

运行前：
    1. 安装 httpx：
           cd /Users/mac/Documents/DevAgent
           .venv/bin/pip install httpx
    2. 在项目根目录运行（脚本会自动读取 DevAgent/.env 里的 CLOSE_ 配置）：
           .venv/bin/python async_lab/step7_llm_concurrent.py

对比思路：
- 并发：总耗时 ≈ 最慢的那一条请求
- 串行：总耗时 ≈ 所有请求耗时之和（脚本会按单条耗时反推给你看，不额外消耗 token）
"""

import asyncio
import time
from pathlib import Path

try:
    import httpx
except ImportError:
    raise SystemExit("请先安装 httpx：cd /Users/mac/Documents/DevAgent && .venv/bin/pip install httpx")

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent


class LLMSettings(BaseSettings):
    # 显式指向项目根目录的 .env，避免受"当前运行目录"影响
    model_config = SettingsConfigDict(
        env_file=ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="CLOSE_",
        extra="ignore",
    )

    llm_base_url: str
    llm_api_key: str
    llm_model: str


settings = LLMSettings()

PROMPTS = [
    "用一句话解释什么是协程。",
    "用一句话解释什么是事件循环。",
    "用一句话解释 async/await 和并发的区别。",
]


async def ask(client: httpx.AsyncClient, prompt: str, index: int) -> dict:
    start = time.perf_counter()
    response = await client.post(
        settings.llm_base_url,
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        json={
            "model": settings.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 100,
        },
        timeout=60,
    )
    response.raise_for_status()
    elapsed = time.perf_counter() - start
    content = response.json()["choices"][0]["message"]["content"]
    return {"index": index, "elapsed": elapsed, "content": content}


async def main():
    print(f"模型：{settings.llm_model}")
    print(f"请求数：{len(PROMPTS)}（并发发出）\n")

    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *(ask(client, prompt, i) for i, prompt in enumerate(PROMPTS, start=1))
        )
    total = time.perf_counter() - start

    for r in results:
        print(f"--- 请求 {r['index']}（耗时 {r['elapsed']:.2f}s）---")
        print(r["content"].strip())
        print()

    serial_estimate = sum(r["elapsed"] for r in results)
    print(f"并发总耗时：{total:.2f}s")
    print(f"如果串行，大约需要：{serial_estimate:.2f}s")
    print("\n要点：")
    print("- 并发总耗时接近最慢的一条，而不是所有耗时之和")
    print("- 这就是为什么 DevAgent 里多个 LLM 调用应该用异步并发")


if __name__ == "__main__":
    asyncio.run(main())
