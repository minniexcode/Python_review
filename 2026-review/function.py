import math

def my_asbtract_function(x):
    '''This function takes a number x and returns its absolute value multiplied by 2.'''
    if x > 0:
        return x * 2
    elif x < 0:
        return -x * 2
    else:
        return 0
    
print(my_asbtract_function(5))
print(my_asbtract_function(-3))
print(my_asbtract_function(0))

def nop():
    pass


def quadratic(a, b, c):
    '''Returns the two solutions of the quadratic equation ax^2 + bx + c = 0.'''
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return 'No real solutions'
    elif discriminant == 0:
        return -b / (2*a)
    else:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return root1, root2
    
def power(x, n=2):
    '''Returns x raised to the power of n.'''
    result = 1
    for _ in range(n):
        result *= x
    return result

# 可变参数

def calculate(*numbers):
    '''Returns the sum of all the numbers passed as arguments.'''
    total = 0
    for number in numbers:
        total += number
    return total

# 关键字参数

def person_info(name, age, **kwargs):
    '''Returns a dictionary containing the person's information.'''
    info = {'name': name, 'age': age}
    info.update(kwargs)
    return info

extra = {'city': 'Beijing', 'job': 'Engineer'}
p1 = person_info('Alice', 30, **extra)
print(p1)

# 命名关键字参数

def person_info2(name, age, *, city, job):
    '''Returns a dictionary containing the person's information.'''
    return {'name': name, 'age': age, 'city': city, 'job': job}

p2 = person_info2('Bob', 25, city='Shanghai', job='Designer')
print(p2)

# 参数组合

def complex_function(a, b=0, *args, c, d=1, **kwargs):
    '''A complex function that demonstrates the use of various types of parameters.'''
    print('a:', a)
    print('b:', b)
    print('args:', args)
    print('c:', c)
    print('d:', d)
    print('kwargs:', kwargs)

complex_function(1, 2, 3, 4, c=5, d=6, extra='value')

'''
小结
Python的函数具有非常灵活的参数形态，既可以实现简单的调用，又可以传入非常复杂的参数。

默认参数一定要用不可变对象，如果是可变对象，程序运行时会有逻辑错误！

要注意定义可变参数和关键字参数的语法：

*args是可变参数，args接收的是一个tuple；

**kw是关键字参数，kw接收的是一个dict。

以及调用函数时如何传入可变参数和关键字参数的语法：

可变参数既可以直接传入：func(1, 2, 3)，又可以先组装list或tuple，再通过*args传入：func(*(1, 2, 3))；

关键字参数既可以直接传入：func(a=1, b=2)，又可以先组装dict，再通过**kw传入：func(**{'a': 1, 'b': 2})。

使用*args和**kw是Python的习惯写法，当然也可以用其他参数名，但最好使用习惯用法。

命名的关键字参数是为了限制调用者可以传入的参数名，同时可以提供默认值。

定义命名的关键字参数在没有可变参数的情况下不要忘了写分隔符*，否则定义的将是位置参数。
'''