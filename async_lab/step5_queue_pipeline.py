"""step5 进阶：asyncio.Queue 生产者-消费者 与 背压

要理解的点：
1. 队列是协程之间安全传递数据的通道
2. maxsize 限制队列长度，队列满时 producer 的 put 会"自动等待"
   —— 这就是背压（backpressure），防止生产太快把内存撑爆
3. 多个消费者会自动分摊任务，天然适合"并发处理"

运行：
    cd /Users/mac/Documents/DevAgent/async_lab
    ../.venv/bin/python step5_queue_pipeline.py
"""

import asyncio
import time

from fake_api import fetch, parse

START = time.perf_counter()
CONSUMER_COUNT = 2


def log(msg: str):
    print(f"[{time.perf_counter() - START:.2f}s] {msg}")


async def producer(queue: asyncio.Queue, n: int):
    for i in range(1, n + 1):
        await queue.put(i)
        log(f"生产者放入 {i}（队列大小 {queue.qsize()}）")
        await asyncio.sleep(0.1)

    # 每个消费者放一个结束标记
    for _ in range(CONSUMER_COUNT):
        await queue.put(None)
    log("生产者结束")


async def consumer(name: str, queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            log(f"{name} 收到结束标记，退出")
            return

        data = await fetch(item, 0.5)
        data = await parse(data)
        log(f"{name} 处理完 {item}（长度 {data['length']}）")
        queue.task_done()


async def main():
    # maxsize=2：队列最多存 2 个，满了生产者会等
    queue: asyncio.Queue = asyncio.Queue(maxsize=2)

    await asyncio.gather(
        producer(queue, n=6),
        *(consumer(f"消费者{i}", queue) for i in range(1, CONSUMER_COUNT + 1)),
    )
    await queue.join()

    print("\n要点：")
    print("- 队列满 → put 等待 → 生产自动降速，这就是背压")
    print("- 多个消费者并发处理，总耗时接近'任务数 / 消费者数 × 单任务耗时'")
    print("- 结束标记（None）是终止消费者的常用手法")


if __name__ == "__main__":
     asyncio.run(main())
