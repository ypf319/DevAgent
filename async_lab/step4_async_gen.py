"""step4 核心：异步生成器 = 流式

这直接对应 LLM 的流式输出（SSE）：
- 普通做法：等全部结果算完，一次性返回
- 异步生成器：每完成一个，就立刻 yield 给调用方

运行：
    cd /Users/mac/Documents/DevAgent/async_lab
    ../.venv/bin/python step4_async_gen.py
"""

import asyncio
import time

from fake_api import fetch

START = time.perf_counter()


def log(msg: str):
    print(f"[{time.perf_counter() - START:.2f}s] {msg}")


async def stream_results(n: int, delay: float = 1.0):
    """异步生成器：完成一个就 yield 一个。"""
    for i in range(1, n + 1):
        data = await fetch(i, delay)
        yield data


async def batch_results(n: int, delay: float = 1.0):
    """对照：全部并发跑完，再一次性返回。"""
    return await asyncio.gather(*(fetch(i, delay) for i in range(1, n + 1)))


async def main():
    print("--- 1. 流式（async for）：完成一个就打印一个 ---")
    async for item in stream_results(3):
        log(f"收到 {item['id']}")

    print("\n--- 2. 批量（gather）：全部完成才一起返回 ---")
    items = await batch_results(3)
    log(f"一次性收到 {[i['id'] for i in items]}")

    print("\n要点：")
    print("- 流式强调'尽早拿到第一份结果'，适合打字机效果、进度条、SSE")
    print("- 批量强调'总耗时最短'，适合结果必须齐全才能继续的场景")
    print("- 两者不冲突：可以流式地消费一个并发批次的完成结果")
    print("- 对应 DevAgent 第四阶段：LLM 流式输出就是 async for + SSE")


if __name__ == "__main__":
    asyncio.run(main())
