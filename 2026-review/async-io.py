"""
asyncio 学习示例（Python 3.4+ 标准库，3.7+ 常用 API 更完整）

这个文件按“由浅入深”的方式演示：
1) 协程基础：async/await
2) 并发任务：create_task / gather / as_completed
3) 超时控制：wait_for
4) 异步协作：Queue（生产者-消费者）
5) 并发限流：Semaphore
6) 混合同步阻塞代码：to_thread
"""

import asyncio
import random
import time


async def basic_coroutine(name: str, delay: float) -> str:
    """
    最基础的协程函数。

    Args:
        name (str): 任务名，用于观察输出。
        delay (float): 模拟 IO 耗时（秒）。

    Returns:
        str: 任务完成后的结果文本。
    """
    print(f"[{name}] start")
    # await 不会阻塞整个线程，只是把控制权交还给事件循环
    await asyncio.sleep(delay)
    print(f"[{name}] done")
    return f"result-{name}"


async def _basic_await_test() -> None:
    """演示 await 的顺序执行：两个协程按顺序等待。"""
    print("\n=== 1) await Ordered Execution ===")
    r1 = await basic_coroutine("A", 0.4)
    r2 = await basic_coroutine("B", 0.2)
    print("ordered results:", r1, r2)


async def _gather_test() -> None:
    """
    演示 asyncio.gather：并发执行多个协程并收集结果。

    说明：
    - gather 会保持“传入顺序”的结果顺序。
    - 适合“我需要所有结果后再继续”的场景。
    """
    print("\n=== 2) gather ===")
    results = await asyncio.gather(
        basic_coroutine("G-1", 0.7),
        basic_coroutine("G-2", 0.3),
        basic_coroutine("G-3", 0.5),
    )
    print("gather results:", results)


async def _task_and_as_completed_test() -> None:
    """
    演示 create_task + as_completed：谁先完成先处理谁。

    适合场景：
    - 任务耗时不均匀，希望“先出结果先消费”，而不是等最慢的任务。
    """
    print("\n=== 3) create_task + as_completed ===")

    tasks = [
        asyncio.create_task(basic_coroutine("C-1", random.uniform(0.2, 0.8))),
        asyncio.create_task(basic_coroutine("C-2", random.uniform(0.2, 0.8))),
        asyncio.create_task(basic_coroutine("C-3", random.uniform(0.2, 0.8))),
    ]

    for done_task in asyncio.as_completed(tasks):
        result = await done_task
        print("as_completed got:", result)


async def _wait_for_timeout_test() -> None:
    """
    演示超时控制：asyncio.wait_for。

    说明：
    - 指定超时后，超过时间会抛出 asyncio.TimeoutError。
    - 在真实项目中常用于“接口超时”“任务超时保护”。
    """
    print("\n=== 4) wait_for Timeout ===")
    try:
        # 这里任务需要 1.2 秒，但只给 0.5 秒，故会超时
        await asyncio.wait_for(basic_coroutine("TIMEOUT", 1.2), timeout=0.5)
    except asyncio.TimeoutError:
        print("task timeout! handled safely.")


async def queue_producer(queue: asyncio.Queue[str], count: int) -> None:
    """生产者：向异步队列中放入数据。"""
    for i in range(count):
        item = f"job-{i}"
        await asyncio.sleep(0.1)
        await queue.put(item)
        print(f"producer -> {item}")


async def queue_consumer(queue: asyncio.Queue[str], worker_name: str) -> None:
    """
    消费者：持续从队列中取数据并处理。

    约定：
    - 当收到 None（哨兵值）时退出循环。
    """
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            print(f"{worker_name} stop")
            return

        await asyncio.sleep(random.uniform(0.1, 0.35))
        print(f"{worker_name} <- {item}")
        queue.task_done()


async def _queue_test() -> None:
    """
    演示 asyncio.Queue 的生产者-消费者模型。

    重点：
    - queue.join() 会等待“所有入队任务都被 task_done() 标记完成”。
    - 用哨兵值让消费者优雅退出。
    """
    print("\n=== 5) Queue Producer Consumer ===")

    queue: asyncio.Queue[str] = asyncio.Queue()
    producer = asyncio.create_task(queue_producer(queue, count=6))
    consumers = [
        asyncio.create_task(queue_consumer(queue, "worker-A")),
        asyncio.create_task(queue_consumer(queue, "worker-B")),
    ]

    await producer
    await queue.join()

    # 给每个消费者发送一个退出哨兵
    for _ in consumers:
        await queue.put(None)
    await asyncio.gather(*consumers)


async def limited_worker(sem: asyncio.Semaphore, idx: int) -> str:
    """受 Semaphore 限制的异步任务。"""
    async with sem:
        print(f"limited-{idx} entered")
        await asyncio.sleep(0.25)
        print(f"limited-{idx} leaving")
        return f"ok-{idx}"


async def _semaphore_test() -> None:
    """
    演示 Semaphore：限制并发度。

    例子：
    - 一次启动 8 个任务，但信号量为 3。
    - 实际同一时刻最多只有 3 个任务进入临界区。
    """
    print("\n=== 6) Semaphore ===")
    sem = asyncio.Semaphore(3)
    tasks = [asyncio.create_task(limited_worker(sem, i)) for i in range(8)]
    results = await asyncio.gather(*tasks)
    print("semaphore results:", results)


def blocking_io_work(seconds: float) -> str:
    """
    模拟同步阻塞函数（例如旧库调用、文件压缩、部分数据库驱动）。

    注意：
    - 如果直接在协程里调用 time.sleep，会阻塞事件循环。
    - 这里配合 asyncio.to_thread 演示如何把阻塞函数扔到线程里执行。
    """
    time.sleep(seconds)
    return f"blocking-done-{seconds}s"


async def _to_thread_test() -> None:
    """演示 asyncio.to_thread：在异步代码中安全执行阻塞函数。"""
    print("\n=== 7) to_thread ===")
    result = await asyncio.to_thread(blocking_io_work, 0.6)
    print("to_thread result:", result)


async def _asyncio_test_all() -> None:
    """串行执行全部 asyncio 示例。"""
    await _basic_await_test()
    await _gather_test()
    await _task_and_as_completed_test()
    await _wait_for_timeout_test()
    await _queue_test()
    await _semaphore_test()
    await _to_thread_test()


if __name__ == "__main__":
    # 统一入口：运行全部示例
    asyncio.run(_asyncio_test_all())
