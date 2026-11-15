"""共享的"假异步服务"。

用 asyncio.sleep 模拟耗时的 I/O 操作（网络请求、读数据库、调用大模型等），
这样所有练习都零依赖、零联网，同时又能真实地产生"等待时间"。
"""

import asyncio


async def fetch(item_id: int, delay: float = 1.0) -> dict:
    """模拟一次 I/O 请求。

    重点对比：
    - time.sleep(delay)      会卡住整个线程，事件循环也跟着停摆
    - await asyncio.sleep(1) 只让出当前协程，事件循环可以继续跑别的协程
    """
    await asyncio.sleep(delay)
    return {
        "id": item_id,
        "text": f"第 {item_id} 条数据",
        "delay": delay,
    }


async def parse(data: dict) -> dict:
    """模拟解析数据：再来一次小的 I/O 等待。"""
    await asyncio.sleep(0.2)
    return {**data, "length": len(data["text"])}
