class Animal:
    '''animal class'''
    
    def __init__(self, name):
        self.name = name

    def say_hello(self):
        print(f'Hello, I am {self.name}')

    def run(self):
        print(f'{self.name} is running...')

# 大类:
class Mammal(Animal):
    pass

class Bird(Animal):
    pass

class RunnableMixin:
    def run(self):
        print(f'{self.name} is running...')
    
class FlyableMixin:
    def fly(self):
        print(f'{self.name} is flying...')


class CarnivorousMixin:
    def eat(self):
        print(f'{self.name} is eating meat...')

class HerbivoresMixin:
    def eat(self):
        print(f'{self.name} is eating grass...')

# 小类:
class Dog(Mammal, RunnableMixin, CarnivorousMixin):
    pass

class Cat(Mammal, RunnableMixin, CarnivorousMixin):
    pass

class Sparrow(Bird, FlyableMixin, HerbivoresMixin):
    pass

class Bat(Bird, FlyableMixin, CarnivorousMixin):
    pass

class Ostrich(Bird, RunnableMixin, HerbivoresMixin):
    pass

class Parrot(Bird, FlyableMixin, HerbivoresMixin):
    pass

