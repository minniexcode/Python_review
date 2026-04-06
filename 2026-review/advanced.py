from collections.abc import Iterable, Iterator
# 切片 slice

l1 = ['Michael', 'Sarah', 'Tracy', 'Bob', 'Jack']

l2 = l1[0:3]
print(l2)

l3 = l1[:3]
print(l3)

l4 = l1[1:3]
print(l4)

l5 = l1[-2:]
print(l5)
l6 = l1[-2:-1]
print(l6)

num_l = list(range(100))
print(num_l)

num_l2 = num_l[:10]
print(num_l2)
num_l3 = num_l[-10:]
print(num_l3)

num_t = tuple(range(20))
print(num_t)
num_t2 = num_t[:10]
print(num_t2)
num_t3 = num_t[-10:]
print(num_t3)

str1 = 'Hello, World!'
str2 = str1[:5]
print(str2)

# 迭代 iterable  
d = {'a': 1, 'b': 2, 'c': 3}
for key in d:
    print(key)

isinstance('abc', str)
isinstance([1, 2, 3], list)
isinstance((1, 2, 3), tuple)
isinstance({'a': 1, 'b': 2, 'c': 3}, dict)
isinstance({1, 2, 3}, set)
b = isinstance('abc', Iterable)

print(b)

i1 = l1.__iter__()
print(i1)

for x in i1:
    print(x)

# 列表生成式 List Comprehensions
L1 = [x * x for x in range(10)]
print(L1)
L2 = [x * x for x in range(10) if x % 2 == 0]
print(L2)
L3 = [m + n for m in 'ABC' for n in 'XYZ']
print(L3)

# 生成器 Generator
g = (x * x for x in range(10))
print(g)

# 创建L和g的区别仅在于最外层的[]和()，L是一个list，而g是一个generator。

def fib(max):
    n, a, b = 0, 0, 1
    while n < max:
        yield b
        a, b = b, a + b
        n += 1

fib_g = fib(10)
print(fib_g)

for x in fib_g:
    print(x)

def odd():
    print('step 1')
    yield 1
    print('step 2')
    yield 3
    print('step 3')
    yield 5

o = odd()
print(o)
print(next(o))
print(next(o))
print(next(o))

# 迭代器 Iterator
i = iter([1, 2, 3])
print(i)

for x in i:
    print(x)

b1 = isinstance(i, Iterator)
print(b1)
b2 = isinstance([], Iterator)
print(b2)
b3 = isinstance({}, Iterator)
print(b3)
b4 = isinstance('abc', Iterator)
print(b4)

# Python的Iterator对象表示的是一个数据流