from .person import Person
from enum import Enum, unique

class Gender(Enum):
    ''' Gender enum '''
    Male = 0
    Female = 1

class Student(Person):
    '''student class'''

    # __slots__ = ('name', 'age', '__score')
    
    def __init__(self, name, age, score):
        '''init method'''
        # class attribute
        name = 'Student'
        super().__init__(name, age)
        self.__score = score

    def say_hello(self):
        print(f'Hello, I am {self.name} and I am {self.age} years old. My score is {self.__score}.')

    def get_grade(self):
        if self.__score >= 90:
            return 'A'
        elif self.__score >= 80:
            return 'B'
        elif self.__score >= 70:
            return 'C'
        elif self.__score >= 60:
            return 'D'
        else:
            return 'E'
    
    def set_score(self, score):
        if 0 <= score <= 100:
            self.__score = score
        else:
            raise ValueError('bad score')
    
    def get_score(self):
        return self.__score
        