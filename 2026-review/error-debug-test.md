# Python 错误处理、调试、单元测试、文档测试笔记

这份笔记按廖雪峰 Python 教程里“错误、调试、测试”这一部分整理，重点不是死记语法，而是理解：

- 程序出错时，Python 到底在做什么
- 我们应该怎么处理错误
- 出了问题怎么定位
- 写完代码后怎么验证它没有坏掉

## 1. 什么是错误

Python 运行时如果遇到不能正常继续的情况，会抛出一个异常（exception）。

比如：

```python
print(10 / 0)
```

会报：

```python
ZeroDivisionError: division by zero
```

这说明：

- 代码执行到了非法操作
- Python 创建了一个异常对象
- 异常开始沿着调用栈向外传播
- 如果没有任何地方处理它，程序就终止

所以异常不是单纯“打印一行红字”，而是一套运行时错误传递机制。

## 2. 常见异常类型

最常见的几种：

- `ZeroDivisionError`：除以 0
- `ValueError`：值的内容不合法
- `TypeError`：类型不对
- `IndexError`：下标越界
- `KeyError`：字典 key 不存在
- `AttributeError`：对象没有这个属性
- `FileNotFoundError`：文件不存在
- `ImportError` / `ModuleNotFoundError`：导入失败

例子：

```python
int('abc')
```

报错：

```python
ValueError: invalid literal for int() with base 10: 'abc'
```

这里不是类型错，而是“字符串这个类型可以转 int，但字符串内容不合法”，所以是 `ValueError`。

## 3. 错误是怎么传播的

看一个例子：

```python
def foo():
    return 10 / 0


def bar():
    return foo()


def main():
    return bar()


main()
```

执行过程：

1. `main()` 调 `bar()`
2. `bar()` 调 `foo()`
3. `foo()` 里发生 `ZeroDivisionError`
4. `foo()` 自己没处理，于是异常往外抛给 `bar()`
5. `bar()` 也没处理，继续往外抛给 `main()`
6. `main()` 还没处理，最终程序退出

这叫异常传播。

所以报错时要意识到：

- 真正出问题的地方，常常在更深的函数里
- 最外层看到的报错，不一定是问题产生的根源位置

## 4. `try...except...finally`

这是 Python 最核心的异常处理结构。

```python
try:
    print('try...')
    r = 10 / 0
    print('result:', r)
except ZeroDivisionError as e:
    print('except:', e)
finally:
    print('finally...')

print('END')
```

执行逻辑：

- 先执行 `try` 里的代码
- 如果没出错，跳过 `except`
- 如果发生匹配的异常，执行 `except`
- 不管有没有异常，最后都执行 `finally`

### 4.1 `except` 的作用

`except` 的作用不是“让错误消失”，而是：

- 接住异常
- 决定如何处理
- 让程序以受控方式继续执行，或者转成更清晰的错误

### 4.2 `finally` 的作用

`finally` 常用于清理资源，比如：

- 关闭文件
- 关闭数据库连接
- 释放锁
- 做必要的收尾

例如：

```python
f = None
try:
    f = open('test.txt', 'r')
    print(f.read())
finally:
    if f:
        f.close()
```

即使中间读文件报错，`finally` 仍然会执行。

## 5. 多个 `except`

不同异常可以分别处理：

```python
try:
    value = int('abc')
    result = 10 / value
except ValueError:
    print('值转换失败')
except ZeroDivisionError:
    print('除数不能为 0')
```

这样做的意义是：

- 不同错误有不同原因
- 不同错误通常应该给不同处理方式

## 6. `else`

`else` 表示：只有 `try` 完全没出错时才执行。

```python
try:
    n = int('123')
except ValueError:
    print('转换失败')
else:
    print('转换成功:', n)
finally:
    print('结束')
```

这个结构适合把“正常逻辑”和“异常逻辑”分开，让代码更清楚。

## 7. 什么时候该捕获异常

不是所有地方都要写 `try/except`。

好的原则是：

- 在你知道怎么处理它的地方捕获
- 在你无法恢复的地方，不要乱吞异常

例如：

- 文件不存在，你可以提示用户重新输入路径，这时适合捕获
- 底层算法逻辑明显错了，这时通常不该随便吞掉异常，而应该让它暴露出来

不推荐这样：

```python
try:
    do_something()
except:
    pass
```

因为这会：

- 隐藏真实问题
- 让 bug 更难查
- 让程序进入一种“看起来没报错，其实已经坏了”的状态

## 8. `raise`：主动抛出异常

异常不一定都是 Python 自动抛的，我们也可以自己抛。

```python
def divide(x, y):
    if y == 0:
        raise ValueError('y cannot be zero')
    return x / y
```

这里的意思是：

- 参数不合法
- 这个函数不接受这种输入
- 调用方必须处理这个问题

### 8.1 为什么要主动 `raise`

因为很多错误属于“业务规则不成立”，不是 Python 语法层面能自动发现的。

例如：

- 年龄不能为负数
- 用户名不能为空
- 转账金额不能小于等于 0

这些都适合主动抛异常。

## 9. 自定义异常

当内置异常不够表达业务语义时，可以自定义。

```python
class UserInputError(ValueError):
    pass


def register(name):
    if not name:
        raise UserInputError('name cannot be empty')
```

这样做的好处：

- 错误语义更清晰
- 上层可以专门捕获这个业务错误
- 不会把所有错误都混在一起

例如：

```python
try:
    register('')
except UserInputError as e:
    print('用户输入错误:', e)
```

## 10. 再抛出异常

有时你想记录一下错误，但不想把它吞掉，可以重新抛出：

```python
try:
    10 / 0
except ZeroDivisionError:
    print('记录日志: 除零错误')
    raise
```

这里的 `raise` 没带参数，表示把当前异常原样继续抛出去。

适合场景：

- 中间层记录日志
- 上层统一处理

## 11. 错误链和“转换异常”

有时底层异常太技术化，上层想转成更清晰的业务错误。

```python
def parse_age(text):
    try:
        return int(text)
    except ValueError as exc:
        raise ValueError('age must be an integer') from exc
```

这里的重点是：

- 外层看到的是更清楚的新错误
- 原始异常信息还保留着
- 这叫异常链

工程里很常见。

## 12. 调试：为什么程序“没按我想的运行”

异常处理解决的是“出错怎么办”，调试解决的是“到底哪里错了”。

Python 常见调试方式有 4 类：

- `print`
- `assert`
- `logging`
- `pdb`

---

## 13. `print` 调试

最简单直接：

```python
def foo(s):
    n = int(s)
    print('n =', n)
    return 10 / n
```

优点：

- 上手最快
- 小脚本很方便

缺点：

- 到处加打印，代码会很乱
- 调试完要手动删
- 输出多了很难看
- 线上程序不适合靠 `print` 排查

所以 `print` 适合学习和快速定位，不适合长期维护。

## 14. `assert` 断言

断言的意思是：我认为这里必须成立，否则程序逻辑就是错的。

```python
def foo(s):
    n = int(s)
    assert n != 0, 'n is zero'
    return 10 / n
```

如果 `n == 0`，会抛：

```python
AssertionError: n is zero
```

### 14.1 `assert` 适合做什么

- 验证开发阶段的假设
- 检查内部不变量
- 快速发现不应该发生的状态

### 14.2 `assert` 不适合做什么

- 不适合代替业务输入校验
- 不适合做用户错误处理

例如：

```python
assert username != ''
```

这不是很好的用户输入校验方式。更合理的是：

```python
if not username:
    raise ValueError('username cannot be empty')
```

### 14.3 为什么说 `assert` 不是正式校验手段

因为 Python 在优化模式下可以关闭断言，所以它更像“开发检查工具”，不是稳定业务规则机制。

## 15. `logging`

比 `print` 更正式的调试和运行记录方式。

```python
import logging

logging.basicConfig(level=logging.INFO)

def foo(s):
    n = int(s)
    logging.info('n = %s', n)
    return 10 / n
```

### 15.1 为什么推荐 `logging`

因为它有等级：

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

可以根据环境控制输出量。

例如：

- 开发环境输出 `DEBUG`
- 生产环境只看 `WARNING` 以上

### 15.2 `logging` 和 `print` 的区别

`print`：

- 只是把内容输出到终端
- 不分级别
- 不方便集中管理

`logging`：

- 可以配置格式
- 可以配置输出位置
- 可以按级别过滤
- 更适合正式项目

### 15.3 一个简单例子

```python
import logging

logging.basicConfig(level=logging.DEBUG)

logging.debug('debug message')
logging.info('info message')
logging.warning('warning message')
logging.error('error message')
```

## 16. `pdb` 单步调试

如果问题比较复杂，只靠打印很难看清，就可以用 Python 自带调试器 `pdb`。

```python
def foo(s):
    n = int(s)
    import pdb; pdb.set_trace()
    return 10 / n
```

程序运行到这里会停下来，进入调试模式。

常用命令：

- `l`：看代码
- `n`：执行下一行
- `p 变量名`：打印变量
- `c`：继续执行
- `q`：退出

### 16.1 `pdb` 的价值

你可以在运行中的程序里：

- 看当前变量值
- 一步步走代码
- 验证逻辑分支是否真的按你想的走

它比到处加 `print` 更强，因为它能“停住现场”。

---

## 17. 单元测试是什么

单元测试就是：

- 针对最小可验证单元写测试
- 通常是函数、方法或类行为
- 自动执行
- 自动判断结果是否符合预期

它的目标不是证明“代码永远没 bug”，而是：

- 防止回归
- 保证改动后已有行为没有被破坏
- 把预期行为写成可执行说明

## 18. `unittest` 的基本结构

Python 标准库自带 `unittest`。

最小例子：

```python
import unittest


def add(x, y):
    return x + y


class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(1, 2), 3)


if __name__ == '__main__':
    unittest.main()
```

这里的结构是：

- 写待测试函数
- 新建一个继承 `unittest.TestCase` 的类
- 每个以 `test_` 开头的方法都是一条测试用例
- `unittest.main()` 负责执行测试

## 19. 常用断言方法

最常用的有：

- `assertEqual(a, b)`
- `assertNotEqual(a, b)`
- `assertTrue(x)`
- `assertFalse(x)`
- `assertIsNone(x)`
- `assertIn(a, b)`
- `assertRaises(ErrorType)`
- `assertAlmostEqual(a, b)`

例如测试异常：

```python
import unittest


def div(x, y):
    return x / y


class TestDiv(unittest.TestCase):
    def test_divide_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            div(10, 0)
```

这里不是看打印，而是明确要求：

- 调用 `div(10, 0)` 必须抛 `ZeroDivisionError`

## 20. `setUp` 和 `tearDown`

如果每个测试前都要准备一些相同数据，可以用：

- `setUp()`：每个测试前执行
- `tearDown()`：每个测试后执行

例如：

```python
import unittest


class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.text = 'python'

    def test_upper(self):
        self.assertEqual(self.text.upper(), 'PYTHON')

    def test_startswith(self):
        self.assertTrue(self.text.startswith('py'))
```

好处是避免重复初始化代码。

## 21. 单元测试到底在测什么

不是测“代码长什么样”，而是测“行为是不是符合预期”。

例如：

```python
def abs_value(n):
    return n if n >= 0 else -n
```

应该测的不是它内部用了 `if` 还是三元表达式，而是：

- 传正数返回正数
- 传负数返回正数
- 传 0 返回 0

也就是说，测试更关注输入输出和行为边界。

## 22. 好的单元测试应该具备什么特点

- 可重复执行
- 不依赖手工输入
- 不依赖运行顺序
- 尽量小而清晰
- 一个测试只验证一个关键点

例如不要在一个测试里同时检查 8 个完全不同的行为，不然失败后很难定位。

## 23. 什么时候要测异常

如果某个函数的预期行为之一就是“遇到非法输入要报错”，那异常本身就应该被测试。

例如：

```python
def parse_score(score):
    if score < 0 or score > 100:
        raise ValueError('score out of range')
    return score
```

那测试里就应该包含：

- 正常输入返回正常值
- 越界输入抛 `ValueError`

## 24. 文档测试 `doctest`

`doctest` 的思想是：

- 把示例写进文档字符串
- 再让 Python 按示例去执行
- 如果结果和文档不一致，就算失败

例子：

```python
def abs_value(n):
    '''
    Return the absolute value of n.

    >>> abs_value(10)
    10
    >>> abs_value(-3)
    3
    >>> abs_value(0)
    0
    '''
    return n if n >= 0 else -n
```

运行方式：

```bash
python -m doctest -v your_file.py
```

### 24.1 `doctest` 的优点

- 文档和测试合一
- 特别适合演示简单函数
- 读者看到的示例就是真正可运行的

### 24.2 `doctest` 的局限

- 不适合复杂测试场景
- 不适合准备很多测试数据的场景
- 对输出格式比较敏感

所以 `doctest` 更适合：

- 教学示例
- 小工具函数
- 简单 API 展示

而复杂逻辑通常还是 `unittest` 更合适。

## 25. `unittest` 和 `doctest` 的区别

### `unittest`

- 更正式
- 更适合项目测试
- 结构更清晰
- 能测试复杂流程和异常场景

### `doctest`

- 更轻量
- 更适合文档示例
- 对学习和小函数很友好

一句话记：

- `unittest` 偏“工程测试”
- `doctest` 偏“文档即示例即测试”

## 26. 错误处理、调试、测试之间的关系

这几个概念不要分开死记，它们是连在一起的。

### 26.1 错误处理

解决的是：

- 程序运行时出错怎么办
- 哪些错误该兜底
- 哪些错误该继续抛出去

### 26.2 调试

解决的是：

- 为什么出错
- 错在什么位置
- 实际执行路径和我想的是不是一样

### 26.3 单元测试

解决的是：

- 修完后会不会再坏
- 改一个地方有没有连带破坏别处

### 26.4 文档测试

解决的是：

- 我写在文档里的示例是不是真的能跑

## 27. 学习时的推荐顺序

建议按这个顺序理解：

1. 先理解异常是什么，怎么传播
2. 学会 `try/except/finally`
3. 学会 `raise` 和自定义异常
4. 再看 `print`、`assert`、`logging`、`pdb`
5. 最后学 `unittest` 和 `doctest`

原因是：

- 先理解“错误机制”
- 再理解“定位错误的方法”
- 最后理解“怎么提前防止错误反复出现”

## 28. 实战建议

### 小脚本或学习代码

- 先用 `print`
- 简单逻辑可加 `assert`
- 出错时看 traceback

### 正式代码

- 不要随便裸 `except`
- 业务错误用 `raise` 明确抛出
- 运行信息尽量用 `logging`
- 核心逻辑写 `unittest`

### 教学和工具文档

- 简单示例可以配 `doctest`

## 29. 一个完整小例子

下面这个例子把“异常、日志、测试”串起来看：

```python
import logging

logging.basicConfig(level=logging.INFO)


class ScoreError(ValueError):
    pass


def parse_score(text):
    logging.info('parse score: %s', text)
    try:
        score = int(text)
    except ValueError as exc:
        raise ScoreError('score must be an integer') from exc

    if score < 0 or score > 100:
        raise ScoreError('score must be between 0 and 100')
    return score
```

这段代码体现了：

- 用 `logging` 记录过程
- 用 `try/except` 处理底层转换异常
- 用自定义异常 `ScoreError` 表达业务语义
- 用 `raise ... from ...` 保留异常链

对应测试可以写：

```python
import unittest


class TestParseScore(unittest.TestCase):
    def test_valid_score(self):
        self.assertEqual(parse_score('90'), 90)

    def test_invalid_text(self):
        with self.assertRaises(ScoreError):
            parse_score('abc')

    def test_out_of_range(self):
        with self.assertRaises(ScoreError):
            parse_score('150')
```

这就形成了一条完整链路：

- 代码遇到异常时有清晰行为
- 调试时有日志可看
- 修改后有测试兜底

## 30. 总结

可以把这一章压缩成下面 4 句话：

1. 异常是 Python 处理运行时错误的机制。
2. `try/except/finally` 让错误处理变得可控。
3. `print`、`assert`、`logging`、`pdb` 是常见调试手段。
4. `unittest` 和 `doctest` 用来验证代码行为，避免回归。

如果再口语一点：

- 异常处理：出错了怎么办
- 调试：到底哪里错了
- 单元测试：修完会不会再坏
- 文档测试：文档里的例子是不是真的能跑
