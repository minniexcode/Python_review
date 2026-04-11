# 多进程

from multiprocessing import Process, Pool, Queue, Pipe
from multiprocessing.connection import PipeConnection
from threading import (
    Thread,
    Lock,
    RLock,
    Condition,
    Event,
    Semaphore,
    BoundedSemaphore,
    Barrier,
)
from collections import deque
import os, time, random


def run_proc(name):
    print("Run child process %s (%s)..." % (name, os.getpid()))


def _process_test():
    print("Parent process %s." % os.getpid())
    p = Process(target=run_proc, args=("test",))
    print("Child process will start.")
    # 启动子进程
    p.start()
    # 等待子进程结束后再继续往下运行，通常用于进程间的同步
    p.join()
    print("Child process end.")


def long_time_task(name):
    print("Run task %s (%s)..." % (name, os.getpid()))
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print("Task %s runs %0.2f seconds." % (name, (end - start)))


def _pool_test():
    print("Parent process will start a pool of workers.")
    # Pool的默认大小是CPU的核数
    pool = Pool()
    print("Pool will start %d processes." % pool._processes)
    for i in range(pool._processes):
        pool.apply_async(long_time_task, args=(i,))
    print("Waiting for all subprocesses done...")
    pool.close()
    pool.join()
    print("All subprocesses done.")


def queue_writer(q: Queue):
    print("Process to write: %s" % os.getpid())
    for value in ["A", "B", "C"]:
        print("Put %s to queue..." % value)
        q.put(value)
        time.sleep(random.random())


def queue_reader(q: Queue):
    print("Process to read: %s" % os.getpid())
    while True:
        value = q.get(True)
        print("Get %s from queue." % value)


def queue_test():
    # 父进程创建Queue，并传给子进程：
    q = Queue()
    pw = Process(target=queue_writer, args=(q,))
    pr = Process(target=queue_reader, args=(q,))
    pw.start()
    pr.start()
    # 等待pw结束
    pw.join()
    # pr进程里是死循环，无法等待其结束，只能强行终止
    pr.terminate()


def send_pipe(conn: PipeConnection):
    print("Process to send: %s" % os.getpid())
    for value in ["A", "B", "C"]:
        print("Send %s to pipe..." % value)
        conn.send(value)
        time.sleep(random.random())


def _pipe_test():
    # Pipe()返回两个连接对象conn1和conn2，分别代表管道的两端
    conn1, conn2 = Pipe()
    p = Process(target=send_pipe, args=(conn1,))
    p.start()
    # 接收子进程发送的数据
    print(conn2.recv())
    # recv()方法是阻塞的，如果子进程还没有发送数据过来，父进程就会一直等待下去，直到子进程发送了数据或者子进程结束了。
    print(conn2.recv())
    print(conn2.recv())
    p.join()


# 多线程


def thread_worker(name: str, delay: float):
    """
    最基础的线程工作函数。

    Args:
        name (str): 线程名，用于日志输出，帮助观察不同线程的执行顺序。
        delay (float): 模拟任务耗时（秒）。

    Returns:
        None: 仅打印日志，不返回值。

    用法说明:
        - 该函数适合作为 Thread(target=...) 的入门示例。
        - 多个线程同时启动时，输出顺序通常不是固定的，这正是并发执行的表现。
    """
    print(f"[{name}] start, pid={os.getpid()}")
    # 用 sleep 模拟耗时操作（例如 IO、网络请求等）
    time.sleep(delay)
    print(f"[{name}] done")


def _thread_basic_test():
    """
    Thread 的基础用法：创建、启动、等待线程。

    Returns:
        None

    逻辑说明:
        1) 构造多个 Thread 对象并传入 target/args。
        2) 统一 start()，让它们并发执行。
        3) 统一 join()，确保主线程等待所有子线程结束。
    """
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


def _lock_test():
    """
    Lock 用法：保护共享变量，避免竞争条件（race condition）。

    Returns:
        None

    逻辑说明:
        - 两个线程都对同一个 counter 进行自增操作。
        - 不加锁时，读改写不是原子操作，结果可能偏小。
        - 使用 lock 后，临界区同一时刻只允许一个线程进入。
    """
    counter = {"value": 0}
    lock = Lock()

    def add_many(n: int):
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


def _rlock_test():
    """
    RLock（可重入锁）用法：同一线程可重复获取同一把锁。

    Returns:
        None

    逻辑说明:
        - outer() 先获取锁，再调用 inner()。
        - inner() 再次获取同一把锁。
        - 这种嵌套加锁场景，普通 Lock 会死锁，RLock 可以安全通过。
    """
    rlock = RLock()

    def inner():
        """演示同一线程二次获取锁。"""
        with rlock:
            print("inner acquired RLock")

    def outer():
        """先拿锁，再调用也会拿同一把锁的 inner。"""
        with rlock:
            print("outer acquired RLock")
            inner()
            print("outer releasing RLock")

    t = Thread(target=outer, name="RLOCK-THREAD")
    t.start()
    t.join()
    print("RLock demo done.")


def _condition_test():
    """
    Condition 用法：实现“生产者-消费者”线程协作。

    Returns:
        None

    逻辑说明:
        - 共享缓冲区为空时，消费者 wait() 进入等待。
        - 生产者放入数据后 notify() 唤醒消费者。
        - 这里使用有限次数，避免演示代码进入无限循环。
    """
    condition = Condition()
    buffer = deque()
    produce_total = 5

    def producer():
        """生产固定数量的数据，并通知消费者。"""
        for i in range(produce_total):
            time.sleep(0.15)
            with condition:
                item = f"item-{i}"
                buffer.append(item)
                print(f"producer -> {item}")
                # 通知一个等待中的消费者可以来取数据了
                condition.notify()

    def consumer():
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


def _event_test():
    """
    Event 用法：一个线程发信号，多个线程感知并继续执行。

    Returns:
        None

    逻辑说明:
        - 工作线程先 wait() 等待“开始信号”。
        - 主线程 set() 后，所有等待线程同时放行。
        - 常用于“统一启动”“就绪通知”“优雅停机”等场景。
    """
    start_event = Event()

    def worker(i: int):
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


def _semaphore_test():
    """
    Semaphore 用法：限制并发访问数量。

    Returns:
        None

    逻辑说明:
        - 假设有 6 个任务，但同一时刻最多只允许 2 个任务进入临界区。
        - 典型场景：数据库连接池、接口限流、固定资源槽位。
    """
    semaphore = Semaphore(2)

    def task(i: int):
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


def _bounded_semaphore_test():
    """
    BoundedSemaphore 用法：防止“过量 release()”的逻辑错误。

    Returns:
        None

    逻辑说明:
        - BoundedSemaphore 与 Semaphore 类似，但会检查上限。
        - 如果 release 次数超过初始值，会抛出 ValueError。
        - 这有助于及早发现并发控制代码中的配对错误。
    """
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


def _barrier_test():
    """
    Barrier 用法：多个线程在某个阶段点“集合”后再继续。

    Returns:
        None

    逻辑说明:
        - 4 个线程先各自准备，准备时间不同。
        - 调用 barrier.wait() 后，所有线程互相等待。
        - 当 4 个线程都到达屏障时，再一起进入下一阶段。
    """
    barrier = Barrier(4)

    def stage_task(i: int):
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


def _threading_test_all():
    """
    串行执行所有 threading 演示，方便一次性学习。

    Returns:
        None
    """
    print("\n=== 1) Thread 基础 ===")
    _thread_basic_test()

    print("\n=== 2) Lock ===")
    _lock_test()

    print("\n=== 3) RLock ===")
    _rlock_test()

    print("\n=== 4) Condition ===")
    _condition_test()

    print("\n=== 5) Event ===")
    _event_test()

    print("\n=== 6) Semaphore ===")
    _semaphore_test()

    print("\n=== 7) BoundedSemaphore ===")
    _bounded_semaphore_test()

    print("\n=== 8) Barrier ===")
    _barrier_test()


if __name__ == "__main__":
    # _process_test()
    # _pool_test()
    # queue_test()
    # _pipe_test()
    _threading_test_all()
