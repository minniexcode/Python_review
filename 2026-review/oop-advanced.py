from object import Teacher
# property

teacher = Teacher('Tom', 30, subject='Math', salary=3000)

teacher.say_hello()
print(f'{teacher.name}\'s subject is {teacher.get_subject()}.')
print(f'{teacher.name}\'s salary is {teacher.salary}.')
teacher.salary = 3500
# teacher.salary = -1000

print(f'{teacher.name}\'s salary is {teacher.salary}.')


# - `__str__`：给人看
# - `__repr__`：给程序员看
# - `__iter__`：声明“我能被遍历”
# - `__next__`：取下一个值
# - `__getitem__`：支持下标和切片

class MyList:
    '''MyList class, support iteration'''

    def __init__(self, data):
        self.data = data
        self.index = 0

    def __str__(self):
        return f'list: {self.data}'

    def __repr__(self):
        return f'MyList({self.data})'

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.data):
            value = self.data[self.index]
            self.index += 1
            return value
        else:
            raise StopIteration
        

my_list = MyList([1, 2, 3, 4, 5])

print(repr(my_list))

print(my_list)

# Enum
from enum import Enum, unique

@unique
class Weekday(Enum):
    '''Weekday enum'''
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

print(Weekday.MONDAY)
print(Weekday.MONDAY.value)

# meta class

class Hello(object):
    def hello(self, name='world'):
        print('Hello, %s.' % name)


h = Hello()
h.hello()

print(type(Hello))
print(type(h))


def fn(self, name='world'):
    print('Hello, %s.' % name)
Hello9 = type('Hello9', (object,), dict(hello=fn)) # 创建Hello class

h9 = Hello9()
h9.hello()


# 用 StringField / IntegerField 解释 metaclass
#
# 1. Field 只是“字段声明对象”，负责描述列名和类型
# 2. ModelMetaclass 在“类创建时”扫描这些字段声明
# 3. Model 再利用元类生成的 __mappings__ 拼出 SQL

class Field:
    def __init__(self, column_name, column_type):
        self.column_name = column_name
        self.column_type = column_type

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.column_name}, {self.column_type}>'


class StringField(Field):
    def __init__(self, column_name):
        super().__init__(column_name, 'varchar(100)')


class IntegerField(Field):
    def __init__(self, column_name):
        super().__init__(column_name, 'bigint')


class ModelMetaclass(type):
    def __new__(mcls, name, bases, attrs):
        # Model 自己只是基类，不需要再被当作 ORM 模型处理。
        if name == 'Model':
            return super().__new__(mcls, name, bases, attrs)

        # mappings 用来保存“模型属性名 -> 字段对象”的对应关系。
        # 例如：name -> StringField('username')
        mappings = {}
        # attrs 是类定义体里的所有属性。
        # 这里要找出所有 Field 实例，把它们从类属性中取出来，单独保存到 mappings。
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                # key 是 Python 里的属性名，比如 name / email
                # value 是字段声明对象，比如 StringField('username')
                mappings[key] = value
                # 从类属性里删掉字段对象，避免它们变成普通类属性。
                attrs.pop(key)

        # 把收集到的字段映射关系挂到类上，供后面 save() 使用。
        attrs['__mappings__'] = mappings
        # 默认把类名转成表名；也可以改成更复杂的命名规则。
        attrs['__table__'] = name.lower()
        # 真正创建类对象。
        return super().__new__(mcls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __getattr__(self, key):
        # 先从实例自己的字典里找属性。
        # 这样 user.name 实际上会读 self['name']。
        try:
            return self[key]
        except KeyError as exc:
            # 如果字典里没有，就抛出标准的属性不存在错误。
            raise AttributeError(f"{self.__class__.__name__} has no attribute {key}") from exc

    def __setattr__(self, key, value):
        # user.name = 'Alice' 实际上就是 self['name'] = 'Alice'。
        self[key] = value

    def save(self):
        # fields 存数据库列名。
        fields = []
        # values 存对应的值。
        values = []
        # placeholders 存 SQL 占位符，避免直接拼接值。
        placeholders = []
        # __mappings__ 是元类提前收集好的字段信息。
        for attr_name, field in self.__mappings__.items():
            # attr_name 是模型属性名，比如 name
            # field.column_name 是数据库列名，比如 username
            fields.append(field.column_name)
            # 从实例里取属性值。
            values.append(getattr(self, attr_name, None))
            placeholders.append('?')

        # 根据字段和占位符拼出一条插入语句。
        sql = f"insert into {self.__table__} ({', '.join(fields)}) values ({', '.join(placeholders)})"
        print('SQL:', sql)
        print('ARGS:', values)


class User(Model):
    id = IntegerField('id')
    # 左边的 name 是 Python 里的“属性名”，右边的字符串是数据库列名 username。
    name = StringField('username')
    email = StringField('email')


user = User(id=1, name='Alice', email='alice@example.com')
print(User.__mappings__)
print(User.__table__)
user.save()



