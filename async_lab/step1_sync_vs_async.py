"""step1 核心：同步 vs 异步串行 vs 异步并发（gather）

这是理解异步编程最关键的一组对照实验：
    同步      time.sleep   × 3  ≈ 3s
    异步串行  await fetch  × 3  ≈ 3s   <-- 注意！async/await 本身不加速
    异步并发  asyncio.gather    ≈ 1s   <-- 并发来自"同时挂到事件循环"

运行：
    cd /Users/mac/Documents/DevAgent/async_lab
    ../.venv/bin/python step1_sync_vs_async.py
"""

import asyncio
import time

from fake_api import fetch

N = 3
DELAY = 1.0


def run_sync():
    """同步串行：time.sleep 会把整个线程卡住。"""
    start = time.perf_counter()
    results = []
    for i in range(1, N + 1):
        time.sleep(DELAY)
        results.append({"id": i})
    return time.perf_counter() - start, results


async def run_async_serial():
    """异步串行：await 只是"让出"，前一个不结束，后一个还是要等。"""
    start = time.perf_counter()
    results = []
    for i in range(1, N + 1):
        results.append(await fetch(i, DELAY))
    return time.perf_counter() - start, results


async def run_async_gather():
    """异步并发：把多个协程同时交给事件循环，等待时间互相重叠。"""
    start = time.perf_counter()
    results = await asyncio.gather(*(fetch(i, DELAY) for i in range(1, N + 1)))
    return time.perf_counter() - start, results


def main():
    print(f"任务数：{N}，每个任务模拟耗时：{DELAY}s\n")

    t_sync, _ = run_sync()
    print(f"1) 同步 time.sleep   ：{t_sync:.2f}s")

    t_serial, _ = asyncio.run(run_async_serial())
    print(f"2) 异步串行 await    ：{t_serial:.2f}s   <-- 没有变快！")

    t_gather, _ = asyncio.run(run_async_gather())
    print(f"3) 异步并发 gather   ：{t_gather:.2f}s   <-- 这才变快")

    print("\n结论：")
    print("- async/await 不等于并发；串行 await 依然是「任务数 × 单次耗时」")
    print("- 并发来自 gather：把多个协程同时挂到事件循环，让等待时间重叠")
    print("- 所以异步的价值在于 I/O 等待期间去干别的事")


if __name__ == "__main__":
    main()
