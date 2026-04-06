from object import Student, Animal, Dog, Cat, Teacher
from models import StudentVO

s = Student('Alice', 20, 95)

s.say_hello()

s_grade = s.get_grade()

print(f'{s.name}\'s grade is {s_grade}.')

# s.set_score(99)

print(s.get_score())


animal = Animal('Animal')
animal.say_hello()
dog = Dog('Dog')
dog.say_hello()
cat = Cat('Cat')
cat.say_hello()


animal.run()
dog.run()
cat.run()

def eat(animal: Animal):
    '''animal eat function'''
    if hasattr(animal, 'eat'):
        animal.eat()
    else:
        print(f'{animal.name} can\'t eat.')

eat(animal)
eat(dog)
eat(cat)


# type, isinstance, dir
print(type(123))
print(type('abc'))
print(type(None))

print(isinstance('abc', str))
print(isinstance(123, int))
# print(dir('ABC'))


# instance attributes and class attributes
Student.school = 'wuhan technology and science university'
print('class attribute:', Student.school)
print('instance attribute:', s.school)
print('student dict', Student.__dict__)
print('s dict', s.__dict__)

svo = StudentVO('Bob', 22, 88)
svo.say_hello()
