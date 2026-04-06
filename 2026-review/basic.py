int1 = 100_000_000_000
print(int1)

str1 = 'hello, world'
print(str1)

# Python还允许用r''表示''内部的字符串默认不转义
str2 = r'hello, \nworld'
print(str2)

str3 = r'''hello,
world'''

bool1 = True
bool2 = False
print(bool1, bool2)
# 布尔值可以用and、or和not运算。
bool3 = bool1 and bool2
bool4 = bool1 or bool2
bool5 = not bool1

print(bool3, bool4, bool5)

a = 123
a = 'ABC'
print(a)

strf = 'hello %s' % 'mininex'

fstr1 = 'hello, i am %s'.format('Codex')

# 最后一种格式化字符串的方法是使用以f开头的字符串，称之为f-string，它和普通字符串不同之处在于，字符串如果包含{xxx}，就会以对应的变量替换：

fstr2 = f'hello, i am {strf}'

classmates = ['Michael', 'Bob', 'Tracy']
print(classmates)

tuple_classmates = ('Michael', 'Bob', 'Tracy')
print(tuple_classmates)

# score is random int
score = 99

match score:
    case 100:
        print('A+')
    case 90:
        print('A')
    case 80:
        print('B')
    case 70:
        print('C')
    case 60:
        print('D')
    case _:
        print('F')

args = ['gcc', 'hello.c', 'world.c']

match args:
    case ['gcc', *files]:
        print('Compiling', files)
    case ['python', *files]:
        print('Running', files)
    case ['ls', *dirs]:
        print('Listing', dirs)
    case _:
        print('Unknown command')

dict1 = {'name': 'Alice', 'age': 20, 'gender': 'female'}

if 'name' in dict1:
    print('name:', dict1['name'])

set1 = {1, 2, 3, 4, 5}
print(set1)

set2 = set([1, 2, 3, 4, 5])
print(set2)

