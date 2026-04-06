from .student import Student
from .animal import Animal, Mammal, Bird, RunnableMixin, FlyableMixin, CarnivorousMixin, HerbivoresMixin, Dog, Cat, Sparrow, Bat, Ostrich, Parrot
from .plant import Plant, Tree, Flower
from .person import Person
from .teacher import Teacher

__author__ = 'ash66'
__all__ = ['Student', 'Person', 'Teacher',
           'Animal', 'Mammal', 'Bird', 'Dog', 'Cat', 
           'Sparrow', 'Bat', 'Ostrich', 'Parrot', 
           'Plant', 'Tree', 'Flower']
# __all__变量是一个list，里面的字符串是模块公开的接口
# 其他模块就可以通过from module import *来导入指定的函数、类和变量
