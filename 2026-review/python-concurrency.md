# Python 并发：进程、线程、协程，从语言机制到工程选型

这篇文章想解决一个很实际的问题：

很多人学 Python 并发时，会看到三套东西一起出现：`multiprocessing`、`threading`、`asyncio`。

然后马上就会产生几个非常真实的疑问：

- 既然有进程和线程，为什么还要协程？
- Python 不是有 GIL 吗，那线程到底还有什么意义？
- `asyncio.Queue`、`queue.Queue`、`multiprocessing.Queue` 名字这么像，到底差在哪里？
- 这些概念到底是工程上的真实需求，还是语言设计在“强行造轮子”？

我这篇文章不打算只讲 API，也不打算把协程神化成“更高级方案”。

我会站在 Python 语言本身的角度，把三件事讲清楚：

1. 它们分别是什么
2. 它们分别解决什么问题
3. 它们在真实工程里该怎么选

文中示例代码来自当前仓库的两个脚本：

- `2026-review/process-thread.py`
- `2026-review/async-io.py`

你可以直接运行：

```bash
python 2026-review/process-thread.py process
python 2026-review/process-thread.py thread
python 2026-review/async-io.py
```

## 先给结论

先把结论摆在最前面，避免读完整篇还抓不到主线。

- 进程不是线程的升级版
- 线程不是协程的过时版
- 协程不是进程和线程的终极替代品

它们只是三种不同的并发模型，各自优化不同的问题。

最短的理解方式是：

- 进程：把任务分给不同的操作系统进程，各自独立，适合 CPU 密集和隔离需求
- 线程：把任务分给同一进程内的多个线程，适合阻塞 IO 和现有同步库
- 协程：把任务交给事件循环，在一个线程里协作切换，适合大量 IO 并发

如果只记一句话，可以记成：

> 进程解决“并行”和“隔离”，线程解决“共享内存下的并发”，协程解决“高并发 IO 下的调度成本”。

## 一张总览表

| 维度 | 进程 | 线程 | 协程 |
| --- | --- | --- | --- |
| 调度者 | 操作系统 | 操作系统 | 事件循环 |
| 是否是 OS 原生执行单元 | 是 | 是 | 否 |
| 默认是否共享内存 | 否 | 是 | 同线程内共享对象 |
| 切换成本 | 高 | 中 | 低 |
| 通信方式 | IPC、Queue、Pipe、Value | 共享对象、Lock、Queue | await、Task、asyncio.Queue |
| CPU 多核利用 | 强 | 在 CPython 中受 GIL 影响 | 单独不能利用多核 |
| IO 高并发能力 | 一般 | 中等 | 很强 |
| 典型代价 | 启动慢、通信重、序列化成本 | 锁、竞态、死锁、GIL | 需要 async 生态、必须显式 await |
| 典型场景 | CPU 密集、隔离任务、并行计算 | 阻塞 IO、传统库、少量并发 | 高并发网络服务、爬虫、网关、异步任务编排 |

## 从 Python 语言本身先看两个事实

很多文章一上来就讲 API，但如果不先理解 Python 自己的约束，很容易把三者看成“谁更先进”。

实际上，Python 并发先天有两个事实必须先接受。

## 事实一：操作系统只认识进程和线程，不认识协程

操作系统原生调度的是：

- 进程
- 线程

协程不是操作系统内核里的执行单位。

协程是语言运行时层面的抽象。对 Python 来说，这个运行时就是：

- `async def` / `await`
- `asyncio` 事件循环
- `Task` 对象

所以协程的“便宜”，不是无代价得来的。

它之所以便宜，是因为它放弃了一些东西：

- 不由操作系统抢占调度
- 只能在 `await` 这类协作点切换
- 依赖整个生态都遵守 async 规则

也就是说，协程是把一部分运行时成本，换成了一部分编程模型成本。

这不是白嫖性能，而是换了一种付费方式。

## 事实二：CPython 有 GIL

绝大多数人用的 Python 都是 CPython。

而 CPython 里有一个非常关键的机制：GIL，Global Interpreter Lock，全局解释器锁。

它的直接影响是：

- 同一时刻，一个 CPython 进程里只能有一个线程执行 Python 字节码

这句话经常被误解成“线程没用”。

这不对。

更准确的理解是：

- 对 CPU 密集型纯 Python 代码，线程通常不能线性吃满多核
- 对 IO 密集型任务，线程仍然很有价值，因为线程在等待系统调用时会释放 GIL
- 对调用 C 扩展的场景，如果扩展内部释放 GIL，线程也可能有不错效果

所以 GIL 改变的是“线程擅长什么”，不是“线程还有没有意义”。

## 没有免费午餐：三种模型各自把代价放在哪儿

如果你对协程天然不信任，这个直觉其实是对的。

因为世界上本来就没有又快、又省、又简单、又通用、还完全兼容旧生态的方案。

三种模型都在付成本，只是成本位置不同。

- 进程把成本放在创建、内存隔离、IPC、序列化
- 线程把成本放在共享状态、锁、竞态条件、死锁、GIL
- 协程把成本放在 async API、事件循环纪律、阻塞调用兼容性、取消语义

这也是为什么“协程不是线程的升级版”。

协程只是把原来由操作系统帮你做的一部分调度，挪到了语言运行时和程序员自己手里。

## 一：进程，Python 里最接近“真并行”的方案

## 进程是什么

进程是操作系统里的资源隔离单位。

每个进程有自己的：

- 地址空间
- 文件描述符状态
- Python 解释器实例
- GIL

这意味着多个 Python 进程之间，彼此不会直接共享普通对象。

这也意味着：

- 一个进程崩了，不一定拖死别的进程
- 多个进程可以真正同时跑在多个 CPU 核心上
- 进程之间通信必须明确使用 IPC 机制

这就是 `multiprocessing` 存在的核心原因。

## Python 为什么需要 `multiprocessing`

在 CPython 世界里，CPU 密集型任务如果想绕开 GIL，最直接的办法就是：

不要让这些任务待在同一个进程里。

于是 Python 标准库给了你 `multiprocessing`。

这套库本质上是：

- 用和 `threading` 类似的编程体验
- 让底层变成多个独立进程

你可以把它理解成：

> Python 没有让线程在 CPU 场景里自然变强，于是给了你一套“用进程模拟线程式开发体验”的标准解法。

## `Process` 的基础用法

在 `2026-review/process-thread.py` 里，我把最基础的 `Process` 示例整理成了这样：

```python
def run_proc(name: str, delay: float = 0.4) -> None:
    print(f"[child:{name}] pid={os.getpid()}, ppid={os.getppid()} start")
    time.sleep(delay)
    print(f"[child:{name}] pid={os.getpid()} done")


def _process_test() -> None:
    print("\n=== 1) Process Basics ===")
    print(f"parent pid={os.getpid()}")

    p = Process(target=run_proc, args=("basic-demo", 0.5), name="PROC-BASIC")
    p.start()
    p.join()
    print(f"child exitcode={p.exitcode}")
```

这个例子最重要的不是 API 本身，而是它说明了三件事：

- `Process(...)` 只是创建对象，不代表子进程已经开始执行
- `start()` 才真正向操作系统申请创建子进程
- `join()` 会让父进程等待子进程结束

如果你刚接触进程，这里一定要注意一个 Python 特性。

在 Windows 上，`multiprocessing` 默认使用 `spawn`。

这会带来两个重要约束：

- 多进程启动代码必须放在 `if __name__ == "__main__":` 下
- 作为 `target` 的函数通常必须定义在模块顶层

否则你经常会遇到子进程反复导入自己、或者对象无法 pickle 的问题。

## `Pool`：真正常用的多进程入口

单个 `Process` 更像教学 API。

真正业务里更常用的是：

- `multiprocessing.Pool`
- `concurrent.futures.ProcessPoolExecutor`

因为现实里的 CPU 任务通常不是“启动一个子进程跑一次”，而是：

- 有一批相似任务
- 想复用固定数量的工作进程
- 让任务自动分发给空闲 worker

我在 `process-thread.py` 里用了一个简单的质数统计任务来模拟 CPU 型工作：

```python
def count_primes(limit: int) -> tuple[int, int, int]:
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
    workloads = [4000, 5000, 6000, 7000]

    with Pool(processes=2) as pool:
        ordered_results = pool.map(count_primes, workloads)
```

这里可以顺便理解两个常用接口：

- `pool.map(func, iterable)`
- `pool.apply_async(func, args=...)`

区别是：

- `map` 更像批处理，一次性扔进去，结果按输入顺序回来
- `apply_async` 更像手动提交任务，拿回 `AsyncResult` 句柄，控制更细

## 进程通信为什么总是显得“麻烦”

因为进程天然就不是共享内存模型。

这恰好是它的优点，也是它的麻烦来源。

优点是：

- 隔离好
- 少很多意外共享状态
- 宕一个不一定全挂

麻烦是：

- 你不能直接把普通 `list`、`dict` 当共享容器来随便改
- 数据要通过 IPC 显式传输
- 很多对象传输时要 pickle，带来序列化成本

## `multiprocessing.Queue`

我把你原先“强制 terminate 消费者”的示例，改成了更适合教学和工程实践的版本：

```python
def queue_writer(q, items: list[str]) -> None:
    for value in items:
        q.put(value)
    q.put(PROCESS_SENTINEL)


def queue_reader(q) -> None:
    while True:
        value = q.get()
        if value is PROCESS_SENTINEL:
            return
        print(f"reader <- {value}")
```

这里最重要的不是 `put()` / `get()` 本身，而是“哨兵值退出”这个习惯。

原因很简单：

- 强制 `terminate()` 常常会中断资源清理
- 子进程可能正持有锁、正在写文件、正在写 socket
- 用哨兵值让消费者自然收尾，才更接近真实可维护代码

## `Pipe`

如果 `Queue` 更像“多人排队取活”，那 `Pipe` 更像“一根直连电话线”。

`process-thread.py` 里的示例：

```python
parent_conn, child_conn = Pipe()
parent_conn.send("hello")
reply = parent_conn.recv()
```

`Pipe` 的特点是：

- 更适合点对点
- 双向通信自然
- 模型简单

但如果你是多个生产者、多个消费者，`Queue` 往往更顺手。

## `Value`：进程也能共享状态，但要显式说明

进程默认不共享普通 Python 对象。

所以如果你确实需要共享少量基础数据，可以用：

- `Value`
- `Array`
- `Manager`

我在脚本里补了一个 `Value` 例子：

```python
shared_counter = Value("i", 0)

def add_to_shared_counter(shared_counter, loops: int) -> None:
    for _ in range(loops):
        with shared_counter.get_lock():
            shared_counter.value += 1
```

这个例子有两个意义：

- 它说明进程默认并不共享普通状态
- 它也说明就算是进程，共享状态时依然可能需要锁

很多人以为“多进程就完全没有并发同步问题”，这也不对。

只是问题位置变了，不是问题消失了。

## 进程适合什么场景

- CPU 密集计算
- 图像处理、视频转码、批量压缩
- 数据分析中可拆分的大计算任务
- 需要进程隔离的爬虫 worker、任务 worker
- 需要真正利用多核的场景

## 进程不太适合什么场景

- 轻量、短小、极高频的小任务
- 需要频繁共享大量复杂对象的场景
- 大量网络连接的高并发 IO 服务

原因不是进程不能做，而是成本通常不划算。

## 二：线程，Python 里最容易落地的并发方案

## 线程是什么

线程是同一进程内部的执行流。

同一进程里的线程：

- 共享内存空间
- 共享大部分进程资源
- 创建成本通常低于进程
- 通信比进程方便得多

线程的魅力就在这里。

你不需要 IPC，就能直接共享：

- `list`
- `dict`
- 类实例
- 缓存对象

但共享越方便，踩坑也越容易。

## `Thread` 的基础用法

`process-thread.py` 里保留并整理了最基础的线程示例：

```python
def thread_worker(name: str, delay: float) -> None:
    print(f"[{name}] start, pid={os.getpid()}")
    time.sleep(delay)
    print(f"[{name}] done")


threads = [
    Thread(target=thread_worker, args=("T-1", 0.8), name="T-1"),
    Thread(target=thread_worker, args=("T-2", 0.4), name="T-2"),
]

for t in threads:
    t.start()
for t in threads:
    t.join()
```

这里最值得观察的一点是：

- 线程和线程之间没有独立的 PID
- 它们共享同一个进程
- 所以日志里 `pid` 一样，但执行顺序会交错

## 线程为什么在 Python 里仍然重要

即便有 GIL，线程依然非常实用。

原因主要有四个：

- 大量传统库就是阻塞式 API
- 阻塞 IO 时线程模型非常自然
- 改造旧代码成本比全量 async 低得多
- 并发量不大时，线程往往是性价比最高的方案

你完全可以把线程理解成：

> Python 里最符合直觉、最兼容现有同步世界、最容易渐进落地的并发模型。

## `queue.Queue`：线程间安全传递任务

你的旧文件里其实没有真正的线程队列示例，只有 `multiprocessing.Queue`。

我这次专门补了一个 `queue.Queue` 版本，方便和 `asyncio.Queue`、`multiprocessing.Queue` 对照。

核心结构是：

```python
work_queue = ThreadQueue()

def producer() -> None:
    for i in range(total_items):
        work_queue.put(f"thread-job-{i}")
    for _ in range(consumer_count):
        work_queue.put(THREAD_SENTINEL)


def consumer(name: str) -> None:
    while True:
        item = work_queue.get()
        if item is THREAD_SENTINEL:
            work_queue.task_done()
            return
        work_queue.task_done()
```

线程 `Queue` 很重要的两个方法是：

- `task_done()`
- `join()`

这里的语义是：

- `put()` 只是“任务入队了”
- `task_done()` 才表示“这个任务真的处理完了”
- `join()` 会等到所有入队任务都被标记完成

这和 `asyncio.Queue` 很像，但它们的等待语义不同，后面会详细讲。

## 线程同步原语：为什么 Python 的 `threading` 内容这么多

因为线程共享内存，所以同步问题一定会跟着来。

你一旦共享可变状态，就绕不开这些原语：

- `Lock`
- `RLock`
- `Condition`
- `Event`
- `Semaphore`
- `BoundedSemaphore`
- `Barrier`

我在 `process-thread.py` 里把这些都整理成了可独立运行的小例子。

下面分别讲一下它们真正解决的问题。

## `Lock`

`Lock` 解决的是最基础的竞争条件。

示例：

```python
counter = {"value": 0}
lock = Lock()

def add_many(n: int) -> None:
    for _ in range(n):
        with lock:
            counter["value"] += 1
```

这里的重点不是“加锁会变慢”，而是：

如果不加锁，`counter += 1` 并不是逻辑上的原子操作。

它背后可能包含：

- 读取旧值
- 计算新值
- 写回结果

多线程交错时就会丢更新。

## `RLock`

`RLock` 是可重入锁。

它解决的不是普通并发，而是“同一线程重复进入同一把锁”的问题。

典型场景是：

- 外层函数已经持有锁
- 内层函数也要持有同一把锁

普通 `Lock` 在这种情况下可能自锁死。

## `Condition`

`Condition` 最适合讲“协作”，而不是“互斥”。

你在脚本里看到的是生产者-消费者：

- 缓冲区为空，消费者等待
- 生产者放入数据后 `notify()` 唤醒消费者

这类问题的本质不是“抢资源”，而是“等某个条件成立”。

## `Event`

`Event` 像一个简单的开关信号。

脚本里的模式是：

- 所有 worker 先 `wait()`
- 主线程 `set()`
- 所有等待线程一起继续

这在工程里很常见：

- 统一启动
- 就绪通知
- 停机信号

## `Semaphore`

`Semaphore` 用来限制同时进入临界区的人数。

它非常适合：

- 连接池
- 接口限流
- 固定槽位资源

和 `Lock` 的区别是：

- `Lock` 通常是 1 个名额
- `Semaphore` 可以是 N 个名额

## `Barrier`

`Barrier` 是阶段同步工具。

几个线程先各自准备，到了某个阶段点，必须等大家都到齐，才能一起进入下一阶段。

这对分阶段处理任务特别有用。

## 线程适合什么场景

- 阻塞 IO
- 少量到中量并发任务
- 需要复用同步库的程序
- 网络请求、磁盘 IO、日志、消费队列
- 不想把整个系统 async 化的项目

## 线程不太适合什么场景

- 大量 CPU 密集型纯 Python 计算
- 极高数量级的并发连接
- 对共享状态错误非常敏感、但团队又不擅长并发同步的场景

## 三：协程，Python 里为高并发 IO 标准化出来的模型

## `asyncio` 到底解决了什么问题

先说最容易说错的一句话。

`asyncio` 不是为了替代进程和线程。

它最核心的目标是：

> 为 Python 提供一套标准化的异步 IO 事件循环模型，让大量“正在等待”的任务不必各占一个线程。

这背后解决的是两个老问题：

- 回调地狱
- 高并发 IO 下线程模型的资源成本

在 `asyncio` 之前，Python 不是不能做异步，而是没有统一标准。

后来：

- Python 3.4 引入 `asyncio`
- Python 3.5 引入 `async` / `await`

这两步结合起来，才让 Python 协程真正可读、可维护、可推广。

所以如果你看到“`asyncio` 是 3.4 引入的”这句话，它是对的。

但也别忘了：

- 真正让协程代码变得像现代 Python 的，是 3.5 的 `async def` / `await`

## 协程到底是什么

在 Python 里，最核心的几层关系是：

- `async def` 定义协程函数
- 调用协程函数，会得到协程对象，但不会立刻执行
- 把协程对象交给事件循环，或 `await` 它，它才会运行
- `asyncio.create_task()` 会把协程包装成事件循环管理的任务

所以协程不是“神秘线程”，它本质上更像：

- 一个可暂停、可恢复的函数
- 在约定好的 `await` 点把控制权交出去

## 一个最小例子

`2026-review/async-io.py` 里最基础的例子是：

```python
async def basic_coroutine(name: str, delay: float) -> str:
    print(f"[{name}] start")
    await asyncio.sleep(delay)
    print(f"[{name}] done")
    return f"result-{name}"
```

这段代码最重要的一行是：

```python
await asyncio.sleep(delay)
```

它表达的不是“睡一下”这么简单，而是：

- 当前协程先挂起
- 把执行权还给事件循环
- 事件循环可以去调度别的协程
- 时间到了再回来继续执行

这就是协程“轻量”的根本。

线程在阻塞等待时，是线程被挂住。

协程在 `await` 时，是协程把控制权主动交回事件循环。

## `gather`：我需要全部结果

`asyncio.gather()` 非常常见：

```python
results = await asyncio.gather(
    basic_coroutine("G-1", 0.7),
    basic_coroutine("G-2", 0.3),
    basic_coroutine("G-3", 0.5),
)
```

它的特点是：

- 并发执行多个协程
- 等所有任务都结束
- 返回值顺序按传入顺序排列

适合场景是：

- 你确实要等所有结果回来再继续下一步

## `create_task` + `as_completed`：谁先回来先处理谁

如果你不想等最慢的那个任务，可以用：

```python
tasks = [
    asyncio.create_task(basic_coroutine("C-1", random.uniform(0.2, 0.8))),
    asyncio.create_task(basic_coroutine("C-2", random.uniform(0.2, 0.8))),
    asyncio.create_task(basic_coroutine("C-3", random.uniform(0.2, 0.8))),
]

for done_task in asyncio.as_completed(tasks):
    result = await done_task
    print(result)
```

这类写法适合：

- 搜索多个来源
- 调多个接口
- 谁先返回谁先处理

它的价值不在“更炫”，而在于吞吐和响应体验更好。

## `wait_for`：超时是协程世界的一等公民

在同步代码里，超时控制往往分散在各个库自己的参数里。

在 `asyncio` 里，超时控制是事件循环层面的常规能力：

```python
await asyncio.wait_for(basic_coroutine("TIMEOUT", 1.2), timeout=0.5)
```

这很重要，因为高并发系统里，最怕的不是任务慢，而是任务永远挂着不收尾。

## `asyncio.Queue`

我在 `async-io.py` 里保留了一个标准的异步生产者-消费者模型：

```python
queue: asyncio.Queue[str] = asyncio.Queue()
producer = asyncio.create_task(queue_producer(queue, count=6))
consumers = [
    asyncio.create_task(queue_consumer(queue, "worker-A")),
    asyncio.create_task(queue_consumer(queue, "worker-B")),
]

await producer
await queue.join()
```

这段代码和线程版 `queue.Queue` 看起来很像，但语义上有一个根本区别：

- `await queue.get()` 挂起的是协程，不是线程

这就是为什么 `asyncio.Queue` 能在一个线程里管理大量等待中的任务。

## `Semaphore`

异步系统非常常见的一种需求是“并发很多，但别一下子全冲出去”。

比如：

- 一次性调 1000 个接口
- 但下游服务只允许同时 50 个请求

所以 `asyncio.Semaphore` 很常见：

```python
sem = asyncio.Semaphore(3)

async def limited_worker(sem: asyncio.Semaphore, idx: int) -> str:
    async with sem:
        await asyncio.sleep(0.25)
        return f"ok-{idx}"
```

这类限流在协程里特别自然，因为调度本来就集中在事件循环里。

## `to_thread`：协程世界不是纯洁世界

很多人一学协程，就容易走向一个极端：

- 认为只要用了 `asyncio`，以后整个世界都该 async

现实完全不是这样。

现实是：

- 你会碰到旧库
- 你会碰到阻塞 API
- 你会碰到无法立刻改造的同步代码

所以 `asyncio.to_thread()` 非常重要：

```python
def blocking_io_work(seconds: float) -> str:
    time.sleep(seconds)
    return f"blocking-done-{seconds}s"


result = await asyncio.to_thread(blocking_io_work, 0.6)
```

这段代码表达了一个非常成熟的工程态度：

- 协程负责高层调度
- 遇到同步阻塞函数，就扔到线程里执行

这也说明：

> Python 并发在真实项目里，常常不是三选一，而是混合使用。

## 现代协程里还应知道 `TaskGroup`

如果你用的是 Python 3.11+，那除了 `gather()`，还应该知道 `TaskGroup`。

它属于更现代的“结构化并发”风格：

```python
async with asyncio.TaskGroup() as tg:
    tg.create_task(fetch_a())
    tg.create_task(fetch_b())
    tg.create_task(fetch_c())
```

它的好处是：

- 任务生命周期更清晰
- 异常传播更规整
- 不容易遗留“后台悬空任务”

本文示例脚本主要用 `gather()` 和 `create_task()`，是为了把基础概念讲得更直接。

但在现代业务代码里，`TaskGroup` 很值得优先考虑。

## 协程适合什么场景

- 高并发网络服务
- 大量 HTTP 请求聚合
- WebSocket、长连接、网关层
- 高并发爬虫
- 异步消息系统客户端
- 需要大量 timeout、cancel、批量调度控制的 IO 系统

## 协程不太适合什么场景

- 纯 CPU 密集计算
- 团队大量依赖同步阻塞库，且短期内不打算改造
- 并发规模其实很小，线程已经足够简单

## 四：三个 Queue，到底差在哪儿

这是最容易“看起来一样，实际上完全不一样”的一组 API。

## 一张对比表

| 类型 | 所属模块 | 主要服务对象 | 等待方式 | 是否跨进程 | 常见搭档 |
| --- | --- | --- | --- | --- | --- |
| `queue.Queue` | `queue` | 线程 | `get()` 阻塞线程 | 否 | `threading.Thread` |
| `multiprocessing.Queue` | `multiprocessing` | 进程 | `get()` 阻塞进程 | 是 | `Process` / `Pool` |
| `asyncio.Queue` | `asyncio` | 协程 | `await get()` 挂起协程 | 否 | `Task` / 事件循环 |

## 最关键的区别：谁在等

你可以把这三个 Queue 的区别压缩成一句话：

> 它们最本质的差异，不是名字，不是方法名，而是“谁在等待”。

具体来说：

- `queue.Queue.get()` 时，等待的是线程
- `multiprocessing.Queue.get()` 时，等待的是进程
- `await asyncio.Queue.get()` 时，等待的是协程

这个区别会直接影响：

- 系统资源消耗
- 调度方式
- 与其它代码的兼容性

## `queue.Queue`

线程版 Queue 的特征是：

- 共享内存模型
- 自带线程安全
- 典型配合 `task_done()` 和 `join()`

它适合的心智模型是：

- 一个进程里有多个线程
- 大家共享对象
- 队列只负责安全传递任务

## `multiprocessing.Queue`

进程版 Queue 的特征是：

- 跨进程通信
- 底层涉及 IPC
- 传输对象通常要 pickle

它适合的心智模型是：

- 多个独立进程之间不能直接共享普通对象
- 所以要用队列作为消息通道

## `asyncio.Queue`

协程版 Queue 的特征是：

- 不跨进程
- 通常也不跨线程
- 只服务于同一事件循环里的协程任务

它最大的意义不是“多一个队列类”，而是：

- 它把等待语义变成了 `await`
- 从而让一个线程里可以管理大量等待中的消费者和生产者

## 五：进程、线程、协程的具体差异，按 12 个维度拆开讲

这部分是整篇文章最核心的比较。

## 1. 调度权在谁手里

- 进程：操作系统调度
- 线程：操作系统调度
- 协程：事件循环调度

这意味着：

- 进程和线程更“抢占式”
- 协程更“协作式”

协程只有在 `await` 等切换点才会让出执行权。

## 2. 是否天然支持多核并行

- 进程：支持
- 线程：在 CPython 纯 Python CPU 代码里受 GIL 影响
- 协程：单独不支持

这点非常重要。

协程能提高并发，但协程本身不等于多核并行。

## 3. 内存模型

- 进程：隔离内存
- 线程：共享内存
- 协程：通常共享同一线程中的对象

这带来的直接后果是：

- 进程最不容易出现“意外共享”
- 线程最容易出现共享状态问题
- 协程虽然通常单线程，但在 `await` 边界上仍可能发生逻辑层面的状态交错

## 4. 通信方式

- 进程：Queue、Pipe、Value、Manager、socket、共享内存
- 线程：共享对象、锁、条件变量、线程队列
- 协程：`await`、`Task`、`asyncio.Queue`、事件循环状态机

进程通信最重，但边界最清晰。

线程通信最直接，但最容易出并发 bug。

协程通信在同一个事件循环里最轻，但只能在 async 生态内自然工作。

## 5. 创建与切换成本

- 进程最高
- 线程次之
- 协程最低

但“协程最低”不是平白得来的。

它的代价是：

- 你必须接受 async 编程范式
- 你必须保证协程里别乱写阻塞调用
- 你必须让下游库也支持 async 或做桥接

## 6. 错误隔离

- 进程最好
- 线程一般
- 协程取决于任务组织方式

为什么说进程最好？

因为进程天生隔离。

线程和协程都在同一个进程里，错误处理更依赖代码组织和资源清理策略。

## 7. 取消和停止能力

这是很多文章容易漏讲的点。

- 进程：可以 `terminate()`，但代价大，清理不一定优雅
- 线程：Python 没有官方安全的“强杀线程”方式，通常只能协作退出
- 协程：原生支持 `cancel()`，但要正确处理 `CancelledError`

这其实是协程很大的一个工程优势。

因为在高并发 IO 系统里，超时和取消是高频需求。

## 8. 超时控制能力

- 进程：更多靠 API 层的 timeout、join(timeout)
- 线程：类似，更多是外围控制
- 协程：`asyncio.wait_for()` 等一等公民 API 更自然

这也是为什么协程很适合网关、聚合服务、爬虫。

## 9. 对阻塞旧库的兼容性

- 进程：很好
- 线程：很好
- 协程：不好，除非桥接

协程最大的问题之一，就是它对生态要求更高。

如果你系统里到处都是阻塞库，那线程往往是更现实的方案。

## 10. 调试复杂度

- 进程：跨进程调试、日志收集、IPC 排查较复杂
- 线程：竞态、死锁、共享状态问题最难查
- 协程：单线程竞争少一些，但容易有“忘记 await”“阻塞事件循环”“悬空任务”之类问题

没有哪一种是天然简单，只是哪种坑你更熟。

## 11. 工程可读性

- 进程：边界明确，数据流相对清晰，但工程胶水较多
- 线程：直觉上容易懂，但锁一多就变复杂
- 协程：基础概念多，但一旦系统是 IO 主导，整体结构可以非常整洁

所以“协程代码看着绕”这个感受并不假。

只是当 IO 并发规模很大时，线程代码往往会更乱。

## 12. 最适合的问题类型

- 进程：CPU 密集、并行计算、隔离 worker
- 线程：阻塞 IO、同步库、少量到中量并发
- 协程：高并发 IO、超时取消控制、事件驱动系统

## 六：`concurrent.futures` 在 Python 并发版图里的位置

很多教程把 `threading`、`multiprocessing`、`asyncio` 分开讲，但真实项目里还有一块经常出现的拼图：

- `concurrent.futures`

它的价值在于：

- 提供统一的 Future 抽象
- 把线程池和进程池包装成更现代的接口

最常见的是：

- `ThreadPoolExecutor`
- `ProcessPoolExecutor`

## 为什么它很重要

因为很多时候你并不需要直接操作：

- `Thread`
- `Process`
- `Pool`

你真正需要的是：

- 提交一批任务
- 拿回 Future
- 等结果
- 统一处理异常

示意代码如下：

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


with ThreadPoolExecutor(max_workers=8) as pool:
    futures = [pool.submit(io_task, item) for item in items]
    for future in futures:
        print(future.result())


with ProcessPoolExecutor(max_workers=4) as pool:
    futures = [pool.submit(cpu_task, item) for item in items]
    for future in futures:
        print(future.result())
```

这套接口的好处是：

- 更统一
- 更适合任务提交式编程
- 容易和上层框架整合

## 它和 `asyncio` 的关系

`asyncio` 不是孤岛，它可以把阻塞代码外包给线程池或进程池。

最常见的桥接方式有两种：

- `asyncio.to_thread()`
- `loop.run_in_executor(...)`

这说明什么？

说明 Python 的真实并发实践，经常是：

- `asyncio` 负责调度 IO
- `ThreadPoolExecutor` 处理阻塞 IO 旧库
- `ProcessPoolExecutor` 处理 CPU 重活

这不是妥协，这是成熟。

## 七：Python 并发的发展脉络

如果不看历史，很容易以为这三套东西是互相竞争的。

其实它们更像是 Python 在不同阶段补不同短板的结果。

## 1. 早期：线程是最直接的并发手段

Python 很早就有线程能力。

因为：

- 操作系统有线程
- 程序员也天然容易理解“开几个线程同时干活”

这阶段的问题是：

- CPU 场景受 GIL 影响
- 共享状态同步复杂

## 2. `multiprocessing`：给 CPU 并行和隔离一个官方答案

后来 Python 标准库提供了 `multiprocessing`。

这基本是在回答一个现实问题：

- 既然线程在 CPython 下不适合纯 Python CPU 并行
- 那就把任务拆去多个进程里跑

于是 Python 有了官方的多进程模型。

## 3. `concurrent.futures`：统一线程池和进程池抽象

再往后，标准库继续往“更统一、更现代的抽象”走，于是有了 `Future` 和 executor。

这一步非常工程化。

它不是发明新并发模型，而是把现有模型用得更顺手。

## 4. `asyncio`：标准化异步 IO

Python 3.4 引入 `asyncio`，这是异步 IO 在标准库层面的里程碑。

它统一了：

- 事件循环
- Future
- Task
- 网络 IO 抽象

但 3.4 时期的协程写法还是基于：

- `yield from`
- `@asyncio.coroutine`

这在工程可读性上不够理想。

## 5. `async` / `await`：协程真正变成人能长期维护的代码

Python 3.5 引入：

- `async def`
- `await`

这一步的重要性非常大。

因为从这一步开始，Python 协程不再只是“能写”，而是“可以作为主流工程风格推广”。

## 6. 3.7 之后：`asyncio.run()` 让入口更清晰

随着版本发展，`asyncio` 的入口和常用 API 也在逐步变得更清晰。

例如：

- `asyncio.run()`
- 更稳定的 task 管理习惯

## 7. 3.9：`to_thread()` 让协程和阻塞世界更好相处

这一步很务实。

它等于官方承认了一件事：

- async 世界不可能完全脱离同步阻塞库

所以干脆给出简单好用的桥接能力。

## 8. 3.11：`TaskGroup` 和结构化并发

Python 3.11 引入 `TaskGroup`、`ExceptionGroup` 等能力。

这代表协程生态在往更强工程可维护性上继续走。

## 9. 3.13 及以后：free-threaded 是方向，但不会让其它模型消失

Python 3.13 开始，官方在推进 free-threaded CPython 的方向，但它目前仍不是默认主流形态，生态也还在适配中。

即使未来这条路成熟，也不代表：

- 进程会消失
- 协程会失去意义

因为：

- 进程解决的不只是 GIL，还有隔离和故障边界
- 协程解决的不只是“线程不够强”，还有海量 IO 等待下的调度成本和超时取消管理

## 八：常见误区

## 误区一：有 GIL，所以线程没用

不对。

更准确的说法是：

- 线程在 CPython 的纯 Python CPU 场景下不适合做重并行计算
- 但在线程等待 IO 时，它依然非常有用

## 误区二：协程更先进，所以以后都该用协程

不对。

协程不是“更先进”，只是“在高并发 IO 场景更合适”。

如果你的项目：

- 并发不大
- 大量同步库
- 团队对 async 不熟

那线程很可能更合理。

## 误区三：进程最清晰，所以能用进程就都用进程

也不对。

进程边界确实清晰，但代价也很真实：

- 启动成本
- 内存成本
- 序列化成本
- IPC 复杂度

这在大量小任务里很可能不划算。

## 误区四：协程没有锁，所以不会有并发问题

不对。

协程减少了操作系统线程层面的抢占式竞争，但不代表不会有逻辑竞态。

如果你在两个 `await` 之间读写共享状态，仍然可能出现时序问题。

## 误区五：三个 Queue 都差不多

不对。

名字像，不代表模型像。

真正的关键是：

- 它服务谁
- 它让谁等待
- 它能不能跨进程

## 九：真实工程里怎么选

这部分给一个非常务实的决策流程。

## 如果你的任务是 CPU 密集型

优先考虑：

- `multiprocessing`
- `ProcessPoolExecutor`

比如：

- 图像处理
- 编码转码
- 批量计算
- 可并行的数据处理

## 如果你的任务是阻塞 IO，而且并发量不大到中等

优先考虑：

- `threading`
- `ThreadPoolExecutor`

比如：

- 同时读写文件
- 调多个阻塞 HTTP 接口
- 调数据库驱动
- 跑一些同步库包装的任务

## 如果你的任务是高并发 IO

优先考虑：

- `asyncio`

比如：

- API 网关
- 高并发爬虫
- WebSocket 服务
- 大量短连接或长连接管理

## 如果你的系统是混合场景

最常见、也最成熟的组合往往是：

- `asyncio` 负责整体调度
- `to_thread()` 或线程池负责阻塞 IO
- 进程池负责 CPU 重活

这类系统不是“不纯”，而是最接近现实。

## 一个简单的选型口诀

可以把选型先粗暴记成：

- 要多核算力，用进程
- 要兼容同步阻塞世界，用线程
- 要高并发网络 IO，用协程

如果还拿不准，再看两件事：

- 任务到底是在算，还是在等
- 你的依赖库到底是同步世界，还是 async 世界

## 十：为什么协程不是“强行造概念”

我最后专门回答一个很常见、也很合理的质疑：

既然线程已经能并发，为什么还要专门造协程？

答案不是“因为协程更高级”，而是：

线程模型在海量 IO 等待场景下，成本真的会变高。

具体表现是：

- 每个线程都要系统级调度
- 每个线程都有栈和上下文成本
- 大量线程下调度和内存占用都会明显上去
- 锁、上下文切换、线程管理复杂度也会增加

而协程说白了就是：

- 这些任务大多数时间都在等
- 既然都在等，不如别给每个等待都配一个线程
- 用一个事件循环管理它们，在 `await` 点协作切换

所以协程不是“发明一个更酷的线程”。

协程是：

- 承认高并发 IO 的主矛盾是等待
- 然后专门为“等待型任务”设计了一种更省资源的调度方式

但它当然也付出了自己的代价。

所以更公平的说法应该是：

> 协程不是想把所有便宜都占了，而是把操作系统层的成本，换成了编程模型层的成本。

## 总结

把整篇文章压缩成最后几句话，就是：

- 进程、线程、协程不是替代关系，而是分工关系
- 进程解决多核并行和隔离
- 线程解决共享内存下的阻塞并发与同步库兼容
- 协程解决高并发 IO 下的资源占用和调度成本
- GIL 让 Python 线程的定位更偏向 IO，而不是纯 Python CPU 并行
- `asyncio` 的意义不是“比线程更先进”，而是“为异步 IO 提供标准化模型”
- 真实工程往往不是三选一，而是组合使用

如果你看完这篇文章，只留下一个最重要的判断标准，那应该是：

> 不要问哪种模型更高级，要问你的任务到底是在“算”，还是在“等”。

算得多，想用多核，优先看进程。

等得多，但库是同步的，优先看线程。

等得多，而且并发量非常大，优先看协程。

这才是 Python 并发真正值得掌握的主线。
