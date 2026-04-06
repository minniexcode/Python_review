from io import StringIO, BytesIO

# file

try:
    with open('./assets/test.txt', 'r') as f:
        print(f.read())
except FileNotFoundError as e:
    print('FileNotFoundError:', e)
finally:
    if f:
        f.close()
    print('finally...')

# StringIO
f = StringIO()
f.write('hello')
f.write(' ')
f.write('world!')

print(f.getvalue())

f1 = StringIO('Hello!\nHi!\nGoodbye!')
while True:
    s = f1.readline()
    if s == '':
        break
    print(s.strip())


# BytesIO

b = BytesIO()
b.write('中文'.encode('utf-8'))
print(b.getvalue())
b1 = BytesIO(b'\xe4\xb8\xad\xe6\x96\x87')
print(b1.read().decode('utf-8'))


# os
import os

print(os.name)
# print(os.umask(0))
print(os.environ)
print(os.path.abspath('.'))

path_list = [x for x in os.listdir('.') if os.path.isdir(x)]
print(path_list)
