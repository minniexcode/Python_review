from .person import Person

class Teacher(Person):
    '''teacher class'''

    def __init__(self, name, age, **kwargs):
        super().__init__(name, age)
        self.__subject = kwargs.get('subject', 'Unknown')
        self._salary = kwargs.get('salary', 2000)


    def say_hello(self):
        print(f'Hello, I am {self.name} and I am {self.age} years old. I teach {self.__subject}.', f'My salary is {self._salary}.')

    def get_subject(self):
        return self.__subject

    @property
    def salary(self):
        return self._salary
    
    @salary.setter
    def salary(self, salary):
        if salary < 0:
            raise ValueError('bad salary')
        self._salary = salary
    