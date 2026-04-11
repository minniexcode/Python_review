"""
Python 并发学习脚本：multiprocessing + threading。

这个文件从“可运行示例”的角度整理了两类并发模型：
1) 多进程：适合 CPU 密集型任务，或需要进程隔离的场景
2) 多线程：适合阻塞 IO、现成同步库、少量并发任务

运行方式：
    python 2026-review/process-thread.py thread
    python 2026-review/process-thread.py process
    python 2026-review/process-thread.py all

说明：
    - Windows 默认使用 spawn 启动子进程，所以多进程代码必须放在
      if __name__ == "__main__": 保护下。
    - 进程 target 最好定义在模块顶层，避免因无法 pickle 而启动失败。
    - 这个脚本更偏教学，因此任务规模较小，重在理解 API 和行为。
"""

from collections import deque
from multiprocessing import (
    Pipe,
    Pool,
    Process,
    Queue as ProcessQueue,
    Value,
    freeze_support,
)
from multiprocessing.connection import Connection
from queue import Queue as ThreadQueue
from threading import (
    Barrier,
    BoundedSemaphore,
    Condition,
    Event,
    Lock,
    RLock,
    Semaphore,
    Thread,
)
import os
import random
import sys
import time


PROCESS_SENTINEL = None
THREAD_SENTINEL = None


# 多进程


def run_proc(name: str, delay: float = 0.4) -> None:
    """
    最基础的子进程工作函数。

    Args:
        name (str): 子进程任务名。
        delay (float): 用 sleep 模拟工作耗时。

    Returns:
        None

    说明：
        - 子进程有自己独立的 PID 和内存空间。
        - 即使执行的是同一个 Python 文件，也已经是新的进程实例了。
    """
    print(f"[child:{name}] pid={os.getpid()}, ppid={os.getppid()} start")
    time.sleep(delay)
    print(f"[child:{name}] pid={os.getpid()} done")


def _process_test() -> None:
    """
    Process 的基础用法：创建、启动、等待、查看退出码。

    Returns:
        None

    逻辑说明：
        1) 父进程创建 Process 对象，但此时子进程还没启动。
        2) 调用 start() 后，操作系统真正创建子进程。
        3) 调用 join() 后，父进程等待子进程执行完。
        4) exitcode 为 0 表示正常退出。
    """
    print("\n=== 1) Process Basics ===")
    print(f"parent pid={os.getpid()}")

    p = Process(target=run_proc, args=("basic-demo", 0.5), name="PROC-BASIC")
    print("child process object created, about to start")
    p.start()
    print(f"child started, child pid={p.pid}")

    # join() 是阻塞等待，确保父进程在这里等子进程结束。
    p.join()
    print(f"child exitcode={p.exitcode}")


def count_primes(limit: int) -> tuple[int, int, int]:
    """
    一个简单的 CPU 风格任务：统计 2..limit 之间的质数个数。

    Args:
        limit (int): 统计上限。

    Returns:
        tuple[int, int, int]: (处理该任务的 pid, limit, 质数数量)

    说明：
        - 这是纯计算任务，几乎不依赖外部 IO。
        - 这种任务更能体现“多进程可以利用多核”的意义。
    """
    total = 0
    for number in range(2, limit + 1):
        is_prime = True
        factor = 2
        while factor * factor <= number:
            if number % factor == 0:
                is_prime = False
                break
            factor += 1
        if is_prime:
            total += 1
    return os.getpid(), limit, total


def _pool_test() -> None:
    """
    Pool 用法：用进程池批量执行任务。

    Returns:
        None

    逻辑说明：
        - Pool 适合“很多相似任务要分发给多个子进程”的场景。
        - map() 更像批处理：传入一组参数，按输入顺序拿回全部结果。
        - apply_async() 更灵活：每次提交一个任务，返回 AsyncResult 句柄。
    """
    print("\n=== 2) Pool ===")
    workloads = [4000, 5000, 6000, 7000]

    with Pool(processes=2) as pool:
        ordered_results = pool.map(count_primes, workloads)

    print("pool.map results (preserves input order):")
    for pid, limit, total in ordered_results:
        print(f"  pid={pid}, limit={limit}, prime_count={total}")

    with Pool(processes=2) as pool:
        async_jobs = [
            pool.apply_async(count_primes, args=(limit,)) for limit in workloads
        ]
        async_results = [job.get() for job in async_jobs]

    print("pool.apply_async results (fetched by AsyncResult.get):")
    for pid, limit, total in async_results:
        print(f"  pid={pid}, limit={limit}, prime_count={total}")


def queue_writer(q, items: list[str]) -> None:
    """
    向 multiprocessing.Queue 写入数据，并在最后发送哨兵值。

    Args:
        q: 进程安全队列。
        items (list[str]): 要发送的数据列表。

    Returns:
        None

    说明：
        - multiprocessing.Queue 适合多生产者/多消费者场景。
        - 进程之间不能像线程那样直接共享普通 list，所以需要 IPC 容器。
    """
    print(f"writer pid={os.getpid()} start")
    for value in items:
        print(f"writer -> {value}")
        q.put(value)
        time.sleep(0.15)

    q.put(PROCESS_SENTINEL)
    print("writer -> SENTINEL")


def queue_reader(q) -> None:
    """
    从 multiprocessing.Queue 读取数据，直到收到哨兵值。

    Args:
        q: 进程安全队列。

    Returns:
        None
    """
    print(f"reader pid={os.getpid()} start")
    while True:
        value = q.get()
        if value is PROCESS_SENTINEL:
            print("reader <- SENTINEL, graceful stop")
            return

        print(f"reader <- {value}")
        time.sleep(0.2)


def queue_test() -> None:
    """
    multiprocessing.Queue 用法：进程间生产者-消费者。

    Returns:
        None

    逻辑说明：
        - 和旧版“强行 terminate 消费者”相比，这里使用哨兵值优雅退出。
        - 这样更适合实际工程，也更容易与 asyncio.Queue / queue.Queue 对比。
    """
    print("\n=== 3) multiprocessing.Queue ===")
    q = ProcessQueue()
    items = ["A", "B", "C", "D"]

    writer = Process(target=queue_writer, args=(q, items), name="PROC-WRITER")
    reader = Process(target=queue_reader, args=(q,), name="PROC-READER")

    writer.start()
    reader.start()
    writer.join()
    reader.join()
    print(f"writer exitcode={writer.exitcode}, reader exitcode={reader.exitcode}")


def pipe_worker(conn: Connection) -> None:
    """
    Pipe 子进程：接收父进程消息并返回处理结果。

    Args:
        conn (Connection): Pipe 一端的连接对象。

    Returns:
        None

    说明：
        - Pipe 更适合“点对点”的双向通信。
        - 如果需要多个生产者/多个消费者，一般 Queue 更自然。
    """
    print(f"pipe worker pid={os.getpid()} start")
    while True:
        message = conn.recv()
        if message is PROCESS_SENTINEL:
            conn.send("child received sentinel, bye")
            conn.close()
            return

        reply = f"child pid={os.getpid()} processed: {str(message).upper()}"
        conn.send(reply)


def _pipe_test() -> None:
    """
    Pipe 用法：双向、点对点通信。

    Returns:
        None

    逻辑说明：
        - Pipe() 返回两个 Connection，分别代表管道两端。
        - send()/recv() 可以双向传输对象。
        - poll(timeout) 可先检查数据是否已到，避免无限等待。
    """
    print("\n=== 4) Pipe ===")
    parent_conn, child_conn = Pipe()
    p = Process(target=pipe_worker, args=(child_conn,), name="PIPE-WORKER")
    p.start()

    # 父进程只保留自己这端连接，child_conn 交给子进程使用。
    child_conn.close()

    for message in ["hello", "python", "pipe"]:
        parent_conn.send(message)
        if parent_conn.poll(1.0):
            print(parent_conn.recv())

    parent_conn.send(PROCESS_SENTINEL)
    if parent_conn.poll(1.0):
        print(parent_conn.recv())

    parent_conn.close()
    p.join()
    print(f"pipe worker exitcode={p.exitcode}")


def add_to_shared_counter(shared_counter, loops: int) -> None:
    """
    使用 multiprocessing.Value 演示“共享状态 + 显式加锁”。

    Args:
        shared_counter: 跨进程共享的整数值。
        loops (int): 自增次数。

    Returns:
        None

    说明：
        - 进程默认不共享普通 Python 对象。
        - Value 提供了可共享的基础数据类型；其内部也带锁对象可用于保护临界区。
    """
    for _ in range(loops):
        with shared_counter.get_lock():
            shared_counter.value += 1


def _shared_value_test() -> None:
    """
    Value 用法：进程间共享简单数据。

    Returns:
        None

    逻辑说明：
        - 两个子进程共同操作同一个共享整数。
        - 如果没有共享内存对象，普通 int 在两个进程里会各有一份拷贝。
    """
    print("\n=== 5) Shared Value ===")
    shared_counter = Value("i", 0)
    loops = 30000

    p1 = Process(
        target=add_to_shared_counter, args=(shared_counter, loops), name="VALUE-A"
    )
    p2 = Process(
        target=add_to_shared_counter, args=(shared_counter, loops), name="VALUE-B"
    )
    p1.start()
    p2.start()
    p1.join()
    p2.join()

    print(f"shared counter={shared_counter.value}, expected={loops * 2}")


def _multiprocessing_test_all() -> None:
    """串行执行全部 multiprocessing 演示。"""
    _process_test()
    _pool_test()
    queue_test()
    _pipe_test()
    _shared_value_test()


# 多线程


def thread_worker(name: str, delay: float) -> None:
    """
    最基础的线程工作函数。

    Args:
        name (str): 线程名，用于日志输出，帮助观察不同线程的执行顺序。
        delay (float): 模拟任务耗时（秒）。

    Returns:
        None: 仅打印日志，不返回值。

    用法说明：
        - 该函数适合作为 Thread(target=...) 的入门示例。
        - 多个线程同时启动时，输出顺序通常不是固定的，这正是并发执行的表现。
    """
    print(f"[{name}] start, pid={os.getpid()}")
    # 用 sleep 模拟耗时操作（例如 IO、网络请求等）
    time.sleep(delay)
    print(f"[{name}] done")


def _thread_basic_test() -> None:
    """
    Thread 的基础用法：创建、启动、等待线程。

    Returns:
        None

    逻辑说明：
        1) 构造多个 Thread 对象并传入 target/args。
        2) 统一 start()，让它们并发执行。
        3) 统一 join()，确保主线程等待所有子线程结束。
    """
    print("\n=== 1) Thread Basics ===")
    threads = [
        Thread(target=thread_worker, args=("T-1", 0.8), name="T-1"),
        Thread(target=thread_worker, args=("T-2", 0.4), name="T-2"),
        Thread(target=thread_worker, args=("T-3", 0.6), name="T-3"),
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print("All basic threads finished.")


def _thread_queue_test() -> None:
    """
    queue.Queue 用法：线程间安全传递任务。

    Returns:
        None

    逻辑说明：
        - queue.Queue 已经自带线程安全控制，通常不需要再为 put/get 额外加 Lock。
        - task_done() + join() 常用于等待“队列中的任务都处理完成”。
        - 这里也使用哨兵值，让消费者线程可以优雅退出。
    """
    print("\n=== 2) queue.Queue ===")
    work_queue = ThreadQueue()
    total_items = 6
    consumer_count = 2

    def producer() -> None:
        """生产固定数量的任务，然后发送退出哨兵。"""
        for i in range(total_items):
            item = f"thread-job-{i}"
            work_queue.put(item)
            print(f"producer -> {item}")
            time.sleep(0.12)

        for _ in range(consumer_count):
            work_queue.put(THREAD_SENTINEL)
        print("producer -> SENTINEL x2")

    def consumer(name: str) -> None:
        """从队列中获取任务；收到哨兵值后退出。"""
        while True:
            item = work_queue.get()
            if item is THREAD_SENTINEL:
                print(f"{name} <- SENTINEL, stop")
                work_queue.task_done()
                return

            time.sleep(random.uniform(0.1, 0.25))
            print(f"{name} <- {item}")
            work_queue.task_done()

    producer_thread = Thread(target=producer, name="THREAD-PRODUCER")
    consumers = [
        Thread(target=consumer, args=("consumer-A",), name="THREAD-CONSUMER-A"),
        Thread(target=consumer, args=("consumer-B",), name="THREAD-CONSUMER-B"),
    ]

    for t in consumers:
        t.start()
    producer_thread.start()

    producer_thread.join()
    work_queue.join()
    for t in consumers:
        t.join()

    print("queue.Queue demo done.")


def _lock_test() -> None:
    """
    Lock 用法：保护共享变量，避免竞争条件（race condition）。

    Returns:
        None

    逻辑说明：
        - 两个线程都对同一个 counter 进行自增操作。
        - 不加锁时，读改写不是原子操作，结果可能偏小。
        - 使用 lock 后，临界区同一时刻只允许一个线程进入。
    """
    print("\n=== 3) Lock ===")
    counter = {"value": 0}
    lock = Lock()

    def add_many(n: int) -> None:
        """循环自增 n 次，每次自增都在锁保护下执行。"""
        for _ in range(n):
            # 进入临界区：读取 -> 修改 -> 写回
            with lock:
                counter["value"] += 1

    t1 = Thread(target=add_many, args=(100000,), name="LOCK-A")
    t2 = Thread(target=add_many, args=(100000,), name="LOCK-B")
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("Lock counter =", counter["value"])


def _rlock_test() -> None:
    """
    RLock（可重入锁）用法：同一线程可重复获取同一把锁。

    Returns:
        None

    逻辑说明：
        - outer() 先获取锁，再调用 inner()。
        - inner() 再次获取同一把锁。
        - 这种嵌套加锁场景，普通 Lock 会死锁，RLock 可以安全通过。
    """
    print("\n=== 4) RLock ===")
    rlock = RLock()

    def inner() -> None:
        """演示同一线程二次获取锁。"""
        with rlock:
            print("inner acquired RLock")

    def outer() -> None:
        """先拿锁，再调用也会拿同一把锁的 inner。"""
        with rlock:
            print("outer acquired RLock")
            inner()
            print("outer releasing RLock")

    t = Thread(target=outer, name="RLOCK-THREAD")
    t.start()
    t.join()
    print("RLock demo done.")


def _condition_test() -> None:
    """
    Condition 用法：实现“生产者-消费者”线程协作。

    Returns:
        None

    逻辑说明：
        - 共享缓冲区为空时，消费者 wait() 进入等待。
        - 生产者放入数据后 notify() 唤醒消费者。
        - 这里使用有限次数，避免演示代码进入无限循环。
    """
    print("\n=== 5) Condition ===")
    condition = Condition()
    buffer = deque()
    produce_total = 5

    def producer() -> None:
        """生产固定数量的数据，并通知消费者。"""
        for i in range(produce_total):
            time.sleep(0.15)
            with condition:
                item = f"item-{i}"
                buffer.append(item)
                print(f"producer -> {item}")
                # 通知一个等待中的消费者可以来取数据了
                condition.notify()

    def consumer() -> None:
        """消费固定数量的数据，若无数据则等待通知。"""
        for _ in range(produce_total):
            with condition:
                while not buffer:
                    # 防止虚假唤醒，因此用 while 检查条件
                    condition.wait()
                item = buffer.popleft()
                print(f"consumer <- {item}")

    tp = Thread(target=producer, name="PRODUCER")
    tc = Thread(target=consumer, name="CONSUMER")
    tc.start()
    tp.start()
    tp.join()
    tc.join()
    print("Condition demo done.")


def _event_test() -> None:
    """
    Event 用法：一个线程发信号，多个线程感知并继续执行。

    Returns:
        None

    逻辑说明：
        - 工作线程先 wait() 等待“开始信号”。
        - 主线程 set() 后，所有等待线程同时放行。
        - 常用于“统一启动”“就绪通知”“优雅停机”等场景。
    """
    print("\n=== 6) Event ===")
    start_event = Event()

    def worker(i: int) -> None:
        """等待事件触发后开始处理任务。"""
        print(f"worker-{i} waiting start signal...")
        start_event.wait()
        print(f"worker-{i} started")
        time.sleep(0.2)
        print(f"worker-{i} finished")

    workers = [Thread(target=worker, args=(i,), name=f"EV-{i}") for i in range(3)]
    for w in workers:
        w.start()

    time.sleep(0.5)
    print("main thread set event!")
    start_event.set()

    for w in workers:
        w.join()
    print("Event demo done.")


def _semaphore_test() -> None:
    """
    Semaphore 用法：限制并发访问数量。

    Returns:
        None

    逻辑说明：
        - 假设有 6 个任务，但同一时刻最多只允许 2 个任务进入临界区。
        - 典型场景：数据库连接池、接口限流、固定资源槽位。
    """
    print("\n=== 7) Semaphore ===")
    semaphore = Semaphore(2)

    def task(i: int) -> None:
        """争抢信号量，成功后执行，结束时自动释放。"""
        with semaphore:
            print(f"sem-task-{i} entered")
            time.sleep(0.3)
            print(f"sem-task-{i} leaving")

    threads = [Thread(target=task, args=(i,), name=f"SEM-{i}") for i in range(6)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Semaphore demo done.")


def _bounded_semaphore_test() -> None:
    """
    BoundedSemaphore 用法：防止“过量 release()”的逻辑错误。

    Returns:
        None

    逻辑说明：
        - BoundedSemaphore 与 Semaphore 类似，但会检查上限。
        - 如果 release 次数超过初始值，会抛出 ValueError。
        - 这有助于及早发现并发控制代码中的配对错误。
    """
    print("\n=== 8) BoundedSemaphore ===")
    bs = BoundedSemaphore(1)
    bs.acquire()
    print("BoundedSemaphore acquired once.")
    bs.release()
    print("BoundedSemaphore released once.")

    try:
        # 第二次 release 会超过初始上限，触发异常
        bs.release()
    except ValueError as e:
        print("BoundedSemaphore caught error:", e)


def _barrier_test() -> None:
    """
    Barrier 用法：多个线程在某个阶段点“集合”后再继续。

    Returns:
        None

    逻辑说明：
        - 4 个线程先各自准备，准备时间不同。
        - 调用 barrier.wait() 后，所有线程互相等待。
        - 当 4 个线程都到达屏障时，再一起进入下一阶段。
    """
    print("\n=== 9) Barrier ===")
    barrier = Barrier(4)

    def stage_task(i: int) -> None:
        """分阶段执行任务，阶段切换处使用屏障同步。"""
        prepare_time = random.uniform(0.1, 0.5)
        time.sleep(prepare_time)
        print(f"barrier-{i} ready, wait at barrier")
        barrier.wait()
        print(f"barrier-{i} pass barrier")

    threads = [Thread(target=stage_task, args=(i,), name=f"BAR-{i}") for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Barrier demo done.")


def _threading_test_all() -> None:
    """串行执行全部 threading 演示，方便一次性学习。"""
    _thread_basic_test()
    _thread_queue_test()
    _lock_test()
    _rlock_test()
    _condition_test()
    _event_test()
    _semaphore_test()
    _bounded_semaphore_test()
    _barrier_test()


def _print_usage() -> None:
    """打印脚本用法。"""
    print("Usage:")
    print("  python 2026-review/process-thread.py thread")
    print("  python 2026-review/process-thread.py process")
    print("  python 2026-review/process-thread.py all")


if __name__ == "__main__":
    freeze_support()

    mode = sys.argv[1].lower() if len(sys.argv) > 1 else "thread"
    if mode == "thread":
        _threading_test_all()
    elif mode == "process":
        _multiprocessing_test_all()
    elif mode == "all":
        _multiprocessing_test_all()
        _threading_test_all()
    else:
        _print_usage()
