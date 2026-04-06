# Functional Programming
from functools import reduce as reduceFunc, wraps, partial

def my_add_function(x, y, addFunc):
    '''Returns the sum of the results of applying addFunc to x and y.'''
    return addFunc(x) + addFunc(y)

my_add = my_add_function(-22, 13, lambda a: abs(a))
print(my_add)

# map/reduce, filter, sorted

list1 = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x**2, list1))
print('squared:', squared)

reduced = reduceFunc(lambda x, y: x + y, squared)
print('reduced:', reduced)

def charToInt(c):
    return ord(c) - ord('0')

chars = ['1', '2', '3']
ints = list(map(charToInt, chars))
print('ints:', ints)

filtered = list(filter(lambda x: x % 2 == 0, list1))
print('filtered:', filtered)


def primes():
    '''Returns a generator that yields prime numbers indefinitely.'''
    D = {}
    q = 2
    while True:
        if q not in D:
            yield q
            D[q * q] = [q]
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1

for prime in primes():
    if prime > 100:
        break
    print(prime)

list2 = [36, 5, -12, 9, -21]
sorted_list = sorted(list2)

sorted_list2 = sorted(list2, key=abs)

print('sorted_list:', sorted_list)
print('sorted_list2:', sorted_list2)

g1 = (x**2 for x in range(10))
print('g1:', list(g1))

student_l = [('Bob', 75), ('Adam', 92), ('Bart', 66), ('Lisa', 88)]

def by_name(t):
    return t[0]
def by_score(t):
    return t[1]

print('sorted by name:', sorted(student_l, key=by_name))
print('sorted by score:', sorted(student_l, key=by_score, reverse=True))

# 匿名函数 lamada

ll1 = list(map(lambda x: x**2, range(10)))
print('ll1:', ll1)

# Decorator 

# 在面向对象（OOP）的设计模式中，decorator被称为装饰模式。
# OOP的装饰模式需要通过继承和组合来实现，而Python除了能支持OOP的decorator外，直接从语法层次支持decorator。
# Python的decorator可以用函数实现，也可以用类实现。

def log(prefix):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kw):
            print('%s %s():' % (prefix, func.__name__))
            return func(*args, **kw)
        return wrapper
    return decorator

@log('DEBUG')
def now():
    '''Returns the current date and time.'''
    print('2024-6-1')

print(now.__name__)
print(now.__doc__)
now()

# 偏函数 partial function

int2 = partial(int, base=2)
int8 = partial(int, base=8)
int16 = partial(int, base=16)

print('int2 ',int2('1000000'))
print('int8 ',int8('1000000'))
print('int16 ',int16('1000000'))

from module import ABC

abc = ABC('Codex')
abc.say_hello()
