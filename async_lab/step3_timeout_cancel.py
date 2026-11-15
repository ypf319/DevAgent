"""step3 核心：超时与取消

要理解的点：
1. asyncio.wait_for 会在超时后自动取消内部任务，并抛出 TimeoutError
2. task.cancel() 只是"发出取消请求"，协程会在下一个 await 处收到 CancelledError
3. finally 里的清理逻辑一定会执行 —— 这就是异步资源释放的关键位置

运行：
    cd /Users/mac/Documents/DevAgent/async_lab
    ../.venv/bin/python step3_timeout_cancel.py
"""

import asyncio
import time

START = time.perf_counter()


def log(msg: str):
    print(f"[{time.perf_counter() - START:.2f}s] {msg}")


async def slow_job(name: str, delay: float):
    log(f"{name} 开始")
    try:
        await asyncio.sleep(delay)
        log(f"{name} 正常结束")
    except asyncio.CancelledError:
        log(f"{name} 收到取消信号")
        raise
    finally:
        log(f"{name} 执行清理（finally）")


async def demo_timeout():
    print("\n--- 1. wait_for 超时 ---")
    try:
        await asyncio.wait_for(slow_job("任务A", delay=5), timeout=2)
    except TimeoutError:
        log("外层捕获到 TimeoutError（任务A 已被自动取消）")


async def demo_cancel():
    print("\n--- 2. 手动 cancel ---")
    task = asyncio.create_task(slow_job("任务B", delay=4))
    await asyncio.sleep(5)
    log("主协程调用 task.cancel()")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        log("await 被取消的任务，抛出 CancelledError")

    print("\n要点：")
    print("- 取消不是'立刻杀死'，而是在下一个 await 点生效")
    print("- 清理逻辑放 finally，确保超时/取消时也能释放资源")


async def main():
    await demo_timeout()
    await demo_cancel()


if __name__ == "__main__":
    asyncio.run(main())
