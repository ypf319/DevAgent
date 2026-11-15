import asyncio
import time

# 模拟假接口
async def fetch(x, t):
    await asyncio.sleep(t)
    return {"raw": str(x)}

async def parse(d):
    return {"length": len(d["raw"])}

START = time.perf_counter()
CONSUMER_COUNT = 2

def log(msg: str):
    print(f"[{time.perf_counter() - START:.2f}s] {msg}")


async def producer(queue: asyncio.Queue, n: int):
    for i in range(1, n + 1):
        await queue.put(i)
        log(f"生产者放入 {i}（队列大小 {queue.qsize()}）")
        await asyncio.sleep(0.1)
    log("✅ 生产者：所有业务任务投放完毕，生产者协程退出")


async def consumer(name: str, queue: asyncio.Queue):
    while True:
        item = await queue.get()
        try:
            log(f"{name} 拿到任务 {item}")
            data = await fetch(item, 0.5)
            data = await parse(data)
            log(f"{name} 处理完 {item}（长度 {data['length']}）")
        finally:
            # 保证无论异常与否，都回执
            queue.task_done()


async def main():
    queue: asyncio.Queue = asyncio.Queue(maxsize=2)

    # 启动消费者
    consumer_tasks = [
        asyncio.create_task(consumer(f"消费者{i}", queue))
        for i in range(1, CONSUMER_COUNT + 1)
    ]

    # 启动生产者
    producer_task = asyncio.create_task(producer(queue, n=6))

    # 等待生产者把所有任务放完
    await producer_task

    log("\n===== 准备 await queue.join()，这里会卡住，直到全部任务处理完成 =====")
    # 重点：join 阻塞在这里！等待所有put进去的任务都 task_done
    await queue.join()
    log("===== ✅ queue.join() 放行！所有业务任务全部处理完毕 =====")

    # # 任务全部做完了，现在主动取消消费者（消费者还在 while True 等待get）
    # for t in consumer_tasks:
    #     t.cancel()
    # await asyncio.gather(*consumer_tasks, return_exceptions=True)

    log("全部流程结束")


if __name__ == "__main__":
    asyncio.run(main())
