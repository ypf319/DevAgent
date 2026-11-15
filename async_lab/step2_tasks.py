"""step2 核心：create_task 手动调度

要理解的点：
1. create_task 只是"把协程登记到事件循环"，创建瞬间任务还没开始跑
2. 当前协程继续向下执行，不会被阻塞
3. 直到遇到 await（让出控制权），事件循环才有机会去跑那些任务

运行：
    cd /Users/mac/Documents/DevAgent/async_lab
    ../.venv/bin/python step2_tasks.py
"""

import asyncio
import time

from fake_api import fetch

START = time.perf_counter()


def log(msg: str):
    print(f"[{time.perf_counter() - START:.2f}s] {msg}")


async def main():
    log("创建 3 个任务（create_task）")
    tasks = [asyncio.create_task(fetch(i, 1.0), name=f"task-{i}") for i in range(1, 4)]

    log("create_task 立刻返回，主协程继续执行，没有被阻塞")
    log(f"此刻任务状态 done：{[t.done() for t in tasks]}")

    # 让出一次事件循环，任务才真正开始跑（跑到各自的 await 处停下）
    await asyncio.sleep(0)
    log(f"sleep(0) 让出后，任务状态 done：{[t.done() for t in tasks]}")

    await asyncio.sleep(1.2)
    log(f"0.5s 后，任务名：{[t.get_name() for t in tasks]}")
    log(f"0.5s 后，任务状态 done：{[t.done() for t in tasks]}")

    # 逐个 await 拿结果（gather 也行）
    results = await asyncio.gather(*tasks)
    log(f"全部完成，结果 id：{[r['id'] for r in results]}")
    log(f"最终任务状态 done：{[t.done() for t in tasks]}")

    print("\n要点：")
    print("- create_task 之后主协程可以继续干别的事，这就是'并发'的起点")
    print("- 没有 await 让出，任务就一直排队；事件循环靠 await 切换协程")


if __name__ == "__main__":
    asyncio.run(main())
