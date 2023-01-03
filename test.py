import time
from pathlib import Path
import shutil
from transporter import Transporter, UserCancelException

if Path('same_dir').exists():
    shutil.rmtree('same_dir')
try:
    Transporter('same_dir', 'same_dir', threading=False)
except UserCancelException as e:
    print(e)

try:
    Transporter('from', 'test.py', threading=False)
except NotADirectoryError as e:
    print(e)

if Path('noexist').exists():
    shutil.rmtree('noexist')
try:
    Transporter('noexist', '', threading=False)
except UserCancelException as e:
    print(e)

path_from = Path('from')
path_to = Path('to')

for i_dir in [path_from, path_to]:
    if not i_dir.exists():
        i_dir.mkdir(parents=True)
    else:
        for element in i_dir.iterdir():
            if element.is_file():
                element.unlink()
            else:
                shutil.rmtree(element)

def make_file(file_name):
    print(f'meke file: {file_name}')
    with (path_from / file_name).open('w') as f:
        for c in f'write: {file_name}':
            f.write(c)
            time.sleep(0.5)

def charwise_copy(file_from, file_to):
    with Path(file_from).open('r') as f:
        data = f.read()

    with Path(file_to).open('w') as f:
        for c in data:
            f.write(c)
            time.sleep(1)

file_names = [f'test{i}' for i in range(10)]

try:
    no_thread = Transporter(path_from, path_to, threading=False)
    for file_name in file_names:
        make_file(file_name)
        no_thread.transport(file_name)
    no_thread.shutdown()
except UserCancelException as e:
    print(e)

path_from = Path('from')
path_to = Path('to')

for i_dir in [path_from, path_to]:
    for element in i_dir.iterdir():
        if element.is_file():
            element.unlink()
        else:
            shutil.rmtree(element)

try:
    with Transporter(path_from, path_to, copy_method=charwise_copy) as transporter:
        for file_name in file_names:
            make_file(file_name)
            transporter.transport(file_name)
except UserCancelException as e:
    print(e)
