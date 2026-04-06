class Plant:
    def __init__(self, name):
        self.name = name

    def grow(self):
        print(f'{self.name} is growing!')

class Tree(Plant):
    def grow(self):
        print(f'{self.name} is growing taller!')
    
class Flower(Plant):
    def grow(self):
        print(f'{self.name} is blooming!')

