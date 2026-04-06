# Python And JavaScript Closure Notes

## 为什么闭包是函数式编程的重点

闭包不是函数式编程的全部，但它确实是核心能力之一，因为它把这几件事连在一起了：

- 函数可以像值一样被返回和传递
- 函数执行结束后，内部状态仍然可以被保留
- 可以不用 class，也能表达“带状态的行为”
- 高阶函数、回调、惰性计算、函数工厂都依赖它

如果只会把函数当作“可复用代码块”，那还只是普通编程。
如果开始把函数当作“可以携带上下文的数据”，就进入函数式思维了。

## 一句话定义

闭包就是：

一个函数，记住了它定义时所在作用域里的变量，即使外层函数已经执行完，这些变量仍然可以被内部函数继续访问。

## 先看最小例子

### Python

```python
def outer():
    x = 10

    def inner():
        return x

    return inner


f = outer()
print(f())  # 10
```

### JavaScript

```javascript
function outer() {
  const x = 10;

  function inner() {
    return x;
  }

  return inner;
}

const f = outer();
console.log(f()); // 10
```

这里的重点不是“返回了一个函数”，而是：

- `outer()` 已经执行完了
- 但是 `inner()` 还能访问 `x`
- 说明 `x` 没有随着外层调用结束而消失

这就是闭包。

## 为什么需要这种设计

如果没有闭包，函数返回后，外层局部变量就完全不可访问了。

那会直接导致很多模式无法成立：

- 函数工厂
- 带配置的回调函数
- 延迟执行
- 装饰器
- 柯里化
- 私有状态封装

闭包解决的问题是：

“我想保留某次函数调用时的上下文，让后续逻辑继续使用它。”

这和对象保存状态很像，但闭包是用函数来做这件事。

## 闭包和 class 的关系

闭包不是 class 的替代品，但它能完成一部分 class 的职责。

例如计数器。

### Python

```python
def make_counter():
    count = 0

    def counter():
        nonlocal count
        count += 1
        return count

    return counter


c = make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3
```

### JavaScript

```javascript
function makeCounter() {
  let count = 0;

  return function counter() {
    count += 1;
    return count;
  };
}

const c = makeCounter();
console.log(c()); // 1
console.log(c()); // 2
console.log(c()); // 3
```

这类代码说明：

- `count` 是私有状态
- 外部不能直接改它
- 只能通过返回的函数去操作它

这就是闭包最典型的用法之一：

用函数封装状态。

## 这和函数式编程为什么关系大

函数式编程强调：

- 函数是一等公民
- 用函数组合逻辑
- 尽量减少共享可变状态
- 更关注变换、组合和抽象

闭包正好提供了关键基础：

### 1. 函数可以携带环境

普通函数只是逻辑。
闭包函数是“逻辑 + 上下文”。

比如：

```python
def multiply_by(n):
    def inner(x):
        return x * n
    return inner


times2 = multiply_by(2)
times3 = multiply_by(3)

print(times2(10))  # 20
print(times3(10))  # 30
```

```javascript
function multiplyBy(n) {
  return function (x) {
    return x * n;
  };
}

const times2 = multiplyBy(2);
const times3 = multiplyBy(3);

console.log(times2(10)); // 20
console.log(times3(10)); // 30
```

这里 `times2` 和 `times3` 只是同一套逻辑的不同实例，但它们保留了不同的上下文。

### 2. 方便构造高阶函数

高阶函数就是：

- 接收函数作为参数
- 返回函数作为结果

闭包让“返回函数”真正有意义，因为返回的不只是代码，还包括定义时的环境。

### 3. 让延迟执行成为可能

你现在先生成一个函数，未来某个时候再执行它。

如果没有闭包，未来执行时就丢失上下文了。

## Python 和 JavaScript 的共同点

两者在闭包设计上非常接近：

- 都支持函数嵌套函数
- 都允许内部函数引用外层变量
- 都会保留定义时的词法作用域
- 都常用来做工厂函数、回调和状态封装

所以你感觉 Python 和 JavaScript 在 functional 逻辑上很像，这个判断是对的。

## 真正的核心概念：词法作用域

闭包背后最重要的不是“函数返回函数”，而是词法作用域。

词法作用域的意思是：

变量的查找，取决于函数定义时所在的位置，而不是调用时所在的位置。

### Python

```python
x = 'global'

def outer():
    x = 'outer'

    def inner():
        return x

    return inner


f = outer()
print(f())  # outer
```

### JavaScript

```javascript
const x = 'global';

function outer() {
  const x = 'outer';

  function inner() {
    return x;
  }

  return inner;
}

const f = outer();
console.log(f()); // outer
```

`inner` 取到的是定义位置附近的 `x`，不是别处同名变量。

## Python 和 JavaScript 的重要差异

虽然思想很像，但细节上有区别。

### 1. Python 修改外层变量需要 `nonlocal`

```python
def outer():
    count = 0

    def inner():
        nonlocal count
        count += 1
        return count

    return inner
```

如果不写 `nonlocal`，Python 会把 `count` 当作 `inner` 的局部变量。

JavaScript 则更直接：

```javascript
function outer() {
  let count = 0;

  return function inner() {
    count += 1;
    return count;
  };
}
```

### 2. Python 闭包里常见 late binding 问题

这是 Python 学闭包时最容易踩坑的地方之一。

```python
funcs = []

for i in range(3):
    funcs.append(lambda: i)

print(funcs[0]())  # 2
print(funcs[1]())  # 2
print(funcs[2]())  # 2
```

原因不是 lambda 特殊，而是闭包捕获的是变量本身，不是当时的值。

循环结束后，`i` 最终是 `2`，所以全都返回 `2`。

常见修正方式：

```python
funcs = []

for i in range(3):
    funcs.append(lambda i=i: i)

print(funcs[0]())  # 0
print(funcs[1]())  # 1
print(funcs[2]())  # 2
```

JavaScript 在 `var` 时代也有类似问题：

```javascript
var funcs = [];

for (var i = 0; i < 3; i++) {
  funcs.push(function () {
    return i;
  });
}

console.log(funcs[0]()); // 3
console.log(funcs[1]()); // 3
console.log(funcs[2]()); // 3
```

但现在通常用 `let`，每次循环块级作用域不同，问题会少很多：

```javascript
const funcs = [];

for (let i = 0; i < 3; i++) {
  funcs.push(function () {
    return i;
  });
}

console.log(funcs[0]()); // 0
console.log(funcs[1]()); // 1
console.log(funcs[2]()); // 2
```

### 3. JavaScript 里闭包大量出现在异步和回调

例如事件处理、Promise、定时器、React Hooks，本质上都大量依赖闭包。

```javascript
function makeLogger(prefix) {
  return function log(message) {
    console.log(prefix + ': ' + message);
  };
}

const appLog = makeLogger('app');
appLog('started');
```

Python 当然也有回调和装饰器，但 JavaScript 由于前端事件和异步模型，闭包的使用密度通常更高。

## 闭包最常见的实际用途

### 1. 函数工厂

根据参数生成不同功能的函数。

```python
def power_of(n):
    return lambda x: x ** n
```

```javascript
function powerOf(n) {
  return (x) => x ** n;
}
```

### 2. 保留配置

```python
def make_logger(prefix):
    def log(message):
        print(f'[{prefix}] {message}')
    return log
```

```javascript
function makeLogger(prefix) {
  return function (message) {
    console.log(`[${prefix}] ${message}`);
  };
}
```

### 3. 装饰器

Python 装饰器本质就是闭包。

```python
def log_calls(fn):
    def wrapper(*args, **kwargs):
        print('calling', fn.__name__)
        return fn(*args, **kwargs)
    return wrapper
```

这里 `wrapper` 闭包住了 `fn`。

### 4. 私有状态

当你不想暴露内部变量，但又想保留状态时，闭包很适合。

## 闭包的代价和注意点

闭包很强，但也不是总该用。

### 1. 隐式状态会降低可读性

如果状态藏得太深，后续维护时不如 class 直观。

### 2. 可变闭包要小心副作用

函数式编程通常偏爱不可变数据。
如果闭包内部频繁修改外层变量，就会更接近“带私有状态的对象”。

### 3. 调试时要知道捕获的是谁

尤其是循环中的变量捕获问题，Python 和 JavaScript 都容易出坑。

## 怎么判断某段代码是不是在用闭包

你可以看两个条件：

- 有没有内部函数
- 内部函数有没有引用外层局部变量

如果都有，基本就是闭包。

## 你可以这样理解 Python 和 JavaScript 的闭包

### Python

- 闭包很常见
- 和装饰器、高阶函数、生成器思维很搭
- 在数据处理、函数工厂、工具函数中很好用
- 修改外层变量时要注意 `nonlocal`

### JavaScript

- 闭包是日常开发高频能力
- 前端事件、异步回调、模块封装、Hooks 都离不开它
- `let` / `const` 出现后，很多闭包陷阱减少了

## 一个非常实用的最终理解

闭包可以看成：

函数 + 词法环境

或者更口语一点：

函数不只是代码，它还背着它出生时周围的变量一起走。

## 总结

- 闭包是函数式编程的重要基础，但不是全部
- 它让函数拥有“记住上下文”的能力
- Python 和 JavaScript 在闭包思想上非常相近
- JavaScript 的闭包在前端和异步场景里更高频
- Python 的闭包在装饰器、函数工厂和局部状态封装里非常常见
- 真正要理解的不是“函数里套函数”，而是“词法作用域 + 环境捕获”


## 装饰器详解

前面已经提到，装饰器是闭包非常经典的应用。

但更精确一点地说：

- 闭包不是装饰器
- 装饰器通常依赖闭包来实现
- 所以装饰器可以看成“闭包在工程里的成熟实践”

闭包解决的是：

- 函数如何记住外层环境

装饰器解决的是：

- 如何在不改原函数内部代码的情况下，给它增加能力

这两者一结合，就形成了装饰器。

## 装饰器最本质的定义

装饰器本质上就是：

- 接收一个函数
- 返回一个新的函数
- 新函数在调用原函数前后，插入额外逻辑

最经典的结构是：

```python
def decorator(fn):
    def wrapper(*args, **kwargs):
        # 调用前
        result = fn(*args, **kwargs)
        # 调用后
        return result
    return wrapper
```

这里最关键的是：

- `wrapper` 是内部函数
- `wrapper` 用到了外层的 `fn`
- 所以 `wrapper` 对 `fn` 形成了闭包

也就是说，装饰器能成立，底层靠的就是闭包。

## 先不要看 `@`，先看原始写法

```python
def log_calls(fn):
    def wrapper(*args, **kwargs):
        print('calling', fn.__name__)
        return fn(*args, **kwargs)
    return wrapper


def add(x, y):
    return x + y


add = log_calls(add)
print(add(2, 3))
```

执行过程是：

1. 把原函数 `add` 传给 `log_calls`
2. `log_calls` 返回一个新的 `wrapper`
3. 新的 `wrapper` 里闭包住了原函数 `fn`
4. 变量 `add` 现在指向的是 `wrapper`
5. 以后调用 `add()`，本质上是在调用包装后的函数

所以装饰器没有魔法，它只是：

```python
add = log_calls(add)
```

## `@decorator` 只是语法糖

Python 写成：

```python
@log_calls
def add(x, y):
    return x + y
```

等价于：

```python
def add(x, y):
    return x + y


add = log_calls(add)
```

所以 `@log_calls` 并没有创造新原理，它只是让这类包装写法更简洁。

## 为什么装饰器对工程特别重要

因为很多逻辑不是“业务逻辑”，但又几乎所有函数都可能需要。

比如：

- 日志
- 计时
- 缓存
- 重试
- 权限校验
- 参数检查

如果把这些东西都塞进每个函数内部：

- 代码会重复
- 函数职责会变乱
- 维护成本会变高

装饰器的价值就是把这些横切逻辑抽离出来，再统一叠加到函数上。

这和函数式编程很契合，因为它强调：

- 把逻辑拆开
- 用组合的方式增强函数
- 尽量让核心业务保持简单

## 一个完整的日志装饰器

```python
from functools import wraps


def log_calls(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        print(f'calling {fn.__name__} with args={args}, kwargs={kwargs}')
        result = fn(*args, **kwargs)
        print(f'{fn.__name__} returned {result}')
        return result
    return wrapper


@log_calls
def multiply(x, y):
    return x * y


print(multiply(3, 4))
```

这个例子里有几个重点。

### 1. `wrapper(*args, **kwargs)`

这样写是为了让装饰器尽量通用。

因为你通常希望它能包装不同参数形式的函数，而不是只能包装固定签名。

### 2. 调用链条

调用 `multiply(3, 4)` 时，实际流程是：

1. 进入 `wrapper`
2. 先打印日志
3. 再调用原函数 `fn(3, 4)`
4. 拿到结果
5. 再打印返回值
6. 最后返回结果

### 3. `@wraps(fn)`

这个很重要。

如果不用 `wraps`，装饰后的函数会丢失一部分元信息，比如：

- `__name__`
- `__doc__`
- 一些调试和反射信息

不用 `wraps` 时：

```python
def log_calls(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    return wrapper
```

那么：

```python
print(multiply.__name__)
```

很可能看到的是 `wrapper`，而不是原来的函数名。

所以工程里写装饰器，基本都应该配 `functools.wraps`。

## 带参数的装饰器为什么更能体现闭包

这是装饰器最值得理解的一层。

比如你希望日志带前缀：

```python
from functools import wraps


def log_with_prefix(prefix):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            print(f'[{prefix}] calling {fn.__name__}')
            return fn(*args, **kwargs)
        return wrapper
    return decorator


@log_with_prefix('APP')
def greet(name):
    print('hello', name)
```

这时结构变成三层：

1. 第一层 `log_with_prefix(prefix)`：接收配置
2. 第二层 `decorator(fn)`：接收原函数
3. 第三层 `wrapper(*args, **kwargs)`：处理真正调用

也就是说：

- `decorator` 闭包住了 `prefix`
- `wrapper` 闭包住了 `fn`
- 同时 `wrapper` 也能用到 `prefix`

这说明闭包不只是“记住一个变量”，而是可以让函数逐层保存上下文。

所以带参数装饰器往往最能帮助你真正理解闭包。

## 装饰器和 JavaScript 的对应关系

虽然 JavaScript 长期没有像 Python 这样成熟的装饰器语法，但思想完全一致。

### JavaScript 的函数包装

```javascript
function logCalls(fn) {
  return function (...args) {
    console.log('calling', fn.name, 'with', args);
    const result = fn(...args);
    console.log('returned', result);
    return result;
  };
}

function add(x, y) {
  return x + y;
}

const wrappedAdd = logCalls(add);
console.log(wrappedAdd(2, 3));
```

这和 Python 装饰器的本质完全一样：

- 传入原函数
- 返回新函数
- 新函数调用原函数
- 新函数闭包住原函数

你可以把它理解成：

- Python：把这种模式正式语法化了
- JavaScript：更多时候直接手写包装函数
- 底层思想：都是高阶函数 + 闭包

## 装饰器适合什么，不适合什么

适合：

- 多个函数都要复用相同增强逻辑
- 你想把日志、计时、缓存这类逻辑抽离出去
- 你想保持业务函数尽量干净

不太适合：

- 逻辑非常简单，直接写更清楚
- 装饰层太多，导致调用链难追踪
- 状态很复杂，其实更适合 class 或独立对象

## 学装饰器时最容易混淆的点

### 1. 分不清谁是谁

要分清三件事：

- 装饰器函数：`log_calls`
- 原函数：`add`
- 包装后返回的新函数：`wrapper`

### 2. 把 `@decorator` 当成魔法

其实它就是：

```python
fn = decorator(fn)
```

带参数时就是：

```python
fn = decorator_factory(config)(fn)
```

### 3. 忘了闭包才是底层原因

如果没有闭包，`wrapper` 根本记不住原函数 `fn`，那装饰器就无法工作。

## 你可以这样总结闭包和装饰器的关系

- 闭包负责“记住外层环境”
- 高阶函数负责“函数接收函数、返回函数”
- 装饰器负责“把增强逻辑包到原函数外面”

所以装饰器不是独立的新魔法，它是：

闭包 + 高阶函数 + 包装模式

## 最后一句话记忆

如果要把这部分压缩成一句话，可以记成：

装饰器就是利用闭包，把一个函数包起来，在不修改原函数代码的前提下，为它增加额外能力。
