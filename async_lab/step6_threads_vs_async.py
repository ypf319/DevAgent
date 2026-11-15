"""step6 进阶：协程 / 线程 / 进程 的边界

要理解的点：
1. I/O 密集：协程和线程都能并发，耗时大幅下降
2. CPU 密集：协程完全帮不上忙（它会阻塞事件循环），线程受 GIL 限制也帮不上忙，
   只有多进程才能真正并行
3. 结论：异步适合 I/O，不适合 CPU

运行：
    cd /Users/mac/Documents/DevAgent/async_lab
    ../.venv/bin/python step6_threads_vs_async.py
"""

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

N = 3
IO_DELAY = 1.0
CPU_N = 5_000_000


def io_sync_work(_):
    """同步阻塞的 I/O：time.sleep 会占住整个线程。"""
    time.sleep(IO_DELAY)
    return "ok"


async def io_coroutine(_):
    """异步 I/O：await 期间把控制权让给事件循环。"""
    await asyncio.sleep(IO_DELAY)
    return "ok"


def cpu_work(n: int) -> int:
    """纯 CPU 计算，函数内部没有任何 await 点。"""
    total = 0
    for i in range(n):
        total += i * i
    return total


def timed(label: str, fn, *args):
    start = time.perf_counter()
    fn(*args)
    elapsed = time.perf_counter() - start
    print(f"{label}：{elapsed:.2f}s")
    return elapsed


def run_threads_io():
    with ThreadPoolExecutor(max_workers=N) as pool:
        list(pool.map(io_sync_work, range(N)))


async def run_async_io():
    await asyncio.gather(*(io_coroutine(i) for i in range(N)))


async def run_async_cpu():
    # cpu_work 里没有 await，协程之间无法切换，gather 也会变成串行
    await asyncio.gather(*(asyncio.to_thread(cpu_work, CPU_N) for _ in range(N)))


async def run_async_cpu_direct():
    async def cpu_coroutine(_):
        return cpu_work(CPU_N)  # 同步调用，直接阻塞事件循环

    await asyncio.gather(*(cpu_coroutine(i) for i in range(N)))


def run_threads_cpu():
    with ThreadPoolExecutor(max_workers=N) as pool:
        list(pool.map(cpu_work, [CPU_N] * N))


def run_processes_cpu():
    with ProcessPoolExecutor(max_workers=N) as pool:
        list(pool.map(cpu_work, [CPU_N] * N))


def main():
    print(f"I/O 任务：{N} 个，每个 {IO_DELAY}s\n")

    timed("1) 线程池做 I/O      ", run_threads_io)
    timed("2) 协程做 I/O        ", lambda: asyncio.run(run_async_io()))

    print(f"\nCPU 任务：{N} 个，每个约 {CPU_N} 次循环")
    timed("3) 单次 CPU 计算     ", cpu_work, CPU_N)

    # 注意：在协程里直接跑同步 CPU 代码，会阻塞事件循环
    timed("4) 协程直接做 CPU    ", lambda: asyncio.run(run_async_cpu_direct()))
    timed("5) to_thread 做 CPU  ", lambda: asyncio.run(run_async_cpu()))
    timed("6) 线程池做 CPU      ", run_threads_cpu)
    timed("7) 进程池做 CPU      ", run_processes_cpu)

    print("\n要点：")
    print("- 协程只解决 '等待'，不解决 '计算'")
    print("- CPU 代码没有 await 点，异步里会串行执行，还会卡住别的协程")
    print("- 线程受 GIL 限制，CPU 密集提升有限；多进程才能真并行")


if __name__ == "__main__":
    main()
