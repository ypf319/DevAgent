# async_lab：异步编程极小实验室

一个零基础友好的异步编程练习项目。核心目标不是"学会用 asyncio 的 API"，而是**亲眼看见异步到底改变了什么**。

所有练习都围绕同一个「假 I/O 服务」展开：`fake_api.fetch()` 用 `asyncio.sleep` 模拟一次耗时请求。这样零依赖、零联网、结果可重复。

---

## 快速开始

```bash
cd /Users/mac/Documents/DevAgent/async_lab

# 核心 1~4（离线，纯标准库）
../.venv/bin/python step1_sync_vs_async.py
../.venv/bin/python step2_tasks.py
../.venv/bin/python step3_timeout_cancel.py
../.venv/bin/python step4_async_gen.py

# 进阶 5~6（离线，纯标准库）
../.venv/bin/python step5_queue_pipeline.py
../.venv/bin/python step6_threads_vs_async.py

# 实战 7（联网，会消耗 token，需先装 httpx）
../.venv/bin/pip install httpx
../.venv/bin/python step7_llm_concurrent.py
```

> step7 需要在**项目根目录**运行（`.venv/bin/python async_lab/step7_llm_concurrent.py`），
> 或者在 async_lab 里用上面的相对路径跑也可以，因为脚本内部用绝对路径定位 `.env`。

---

## 文件说明

| 文件 | 主题 | 关键问题 |
|---|---|---|
| `fake_api.py` | 共享的假异步服务 | `await asyncio.sleep` 和 `time.sleep` 差在哪？ |
| `step1_sync_vs_async.py` | 同步 / 异步串行 / gather | 为什么"用了 async"还是不变快？ |
| `step2_tasks.py` | `create_task` 调度 | 任务是什么时候开始跑的？ |
| `step3_timeout_cancel.py` | 超时 / 取消 / 清理 | 协程被取消时，资源怎么释放？ |
| `step4_async_gen.py` | 异步生成器 / 流式 | 怎么做到"边算边出结果"？ |
| `step5_queue_pipeline.py` | Queue / 生产者-消费者 / 背压 | 生产太快怎么办？ |
| `step6_threads_vs_async.py` | 协程 / 线程 / 进程 | 什么时候异步帮不上忙？ |
| `step7_llm_concurrent.py` | 并发调用 LLM | 并发和串行的总耗时差多少？ |

---

## 核心概念速查

| 概念 | 一句话解释 |
|---|---|
| 协程（coroutine） | `async def` 定义的函数，调用它不会执行，只会得到一个协程对象 |
| `await` | 把控制权交还事件循环，等这个操作完成后再回来 |
| 事件循环（event loop） | 一个"调度员"，在多个协程之间来回切换 |
| `asyncio.run(main())` | 启动事件循环并运行主协程，程序入口 |
| `asyncio.gather(...)` | 把多个协程同时挂到循环上，实现并发 |
| `asyncio.create_task(...)` | 把协程登记成任务，立刻返回，不阻塞当前协程 |
| `asyncio.sleep(0)` | 主动让出一次控制权，让其他任务有机会运行 |
| `wait_for(..., timeout=)` | 超时后自动取消任务并抛 `TimeoutError` |
| `async for` | 消费异步生成器，来一个处理一个 |
| 背压 | 队列满了让生产者等待，避免内存无限增长 |

---

## 每步的预期现象

### step1：最重要的对照

```text
1) 同步 time.sleep   ：≈ 3.0s
2) 异步串行 await    ：≈ 3.0s   <-- 反直觉：没有变快
3) 异步并发 gather   ：≈ 1.0s   <-- 并发才变快
```

记住这句话：**`async/await` 只是"能并发"的前提，`gather` 才是"真的并发"。**

### step2：任务调度

- `create_task` 之后，`done()` 全是 `False`，主协程继续往下走
- `await asyncio.sleep(0)` 之后任务才真正开始跑
- 0.5s 时任务仍未完成，1s 后全部完成

### step3：超时与取消

- `wait_for(..., timeout=2)` 在约 2s 时抛 `TimeoutError`
- 手动 `cancel()` 后，协程在下一个 `await` 点收到 `CancelledError`
- 两次都会执行 `finally` 里的清理日志

### step4：流式 vs 批量

- 流式：约 1s、2s、3s 各打印一条
- 批量：约 1s 后一次性打印三条

### step5：队列流水线

- 队列大小始终不超过 `maxsize=2`
- 两个消费者轮流处理，日志交错
- 生产者会在队列满时被迫等待

### step6：异步的边界

- I/O：线程池 ≈ 协程 ≈ 1s
- CPU：协程直接做 ≈ 串行；线程池受 GIL 限制提升有限；进程池明显更快

### step7：LLM 并发

- 每条请求单独耗时 1~N 秒不等
- 并发总耗时 ≈ 最慢的那条
- 打印的「如果串行」约等于所有耗时之和

---

## 学习闭环（建议每步都做）

1. **先预测**：运行前写下你觉得会发生什么（耗时、顺序）
2. **再运行**：执行脚本看实际结果
3. **找差异**：和预测不一样的地方，就是理解加深的地方
4. **改参数**：调整任务数、`delay`、`maxsize`，再跑一遍
5. **写结论**：用一句话解释为什么

### 实验记录模板

```text
日期：
练习：stepX
预测：
实际：
差异原因：
一句话结论：
```

---

## 常见坑

1. **只写 `async def` 不 await**：协程对象创建了但从未执行，Python 会警告 "coroutine was never awaited"
2. **在协程里调用阻塞函数**：`time.sleep`、`requests.get`、大循环计算都会卡死整个事件循环
3. **`create_task` 后不保存引用**：任务可能被垃圾回收，官方建议用变量或集合持有引用
4. **以为 async 能加速 CPU 计算**：不会，CPU 密集请用多进程
5. **`gather` 和 `as_completed` 混淆**：`gather` 按传入顺序返回；`as_completed` 谁先完成先处理
6. **忘记处理取消**：长时间任务要在 `finally` 里释放资源（连接、文件、锁）

---

## 与 DevAgent 的衔接

| 本练习 | DevAgent 里的对应场景 |
|---|---|
| `step4` 异步生成器 | 第四阶段 LLM 流式输出（SSE、打字机效果） |
| `step6` 异步的边界 | 判断哪些同步调用该换成异步（网络/文件），哪些不该 |
| `step7` 并发调用 | 并行检索 + 生成、一次问多个模型、批量评测 |
| `step1` 的对照 | 理解为什么现在的 `requests` 串行调用慢 |

---

## 参考：一次完整的运行输出

```text
$ ../.venv/bin/python step1_sync_vs_async.py
任务数：3，每个任务模拟耗时：1.0s

1) 同步 time.sleep   ：3.00s
2) 异步串行 await    ：3.00s   <-- 没有变快！
3) 异步并发 gather   ：1.00s   <-- 这才变快

结论：
- async/await 不等于并发；串行 await 依然是「任务数 × 单次耗时」
- 并发来自 gather：把多个协程同时挂到事件循环，让等待时间重叠
- 所以异步的价值在于 I/O 等待期间去干别的事
```
