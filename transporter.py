from pathlib import Path
from shutil import copy2
from concurrent.futures import ThreadPoolExecutor

class UserCancelException(BaseException):
    def __init__(self, msg='UserCancelException'):
        self.msg = msg
    
    def __str__(self):
        return self.msg
    
    def __repr__(self):
        return self.msg

class DummyExecutor:
    def submit(self, fn, /, *args, **kwargs):
        fn(*args, **kwargs)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False
    
    def shutdown(self, wait=True, *, cance_futures=False):
        pass

def fun_delete(file_name):
    Path(file_name).unlink()

class Transporter:
    def __init__(self, path_from, path_to, confirm=True, 
            copy_method=copy2, del_method=fun_delete, threading=True):

        self.path_from = Path(path_from).resolve()
        self.path_to = Path(path_to).resolve()

        def decorate_copy(method):
            def copy_method2(file_path_from, file_path_to):
                print('copy file \n' \
                    f'from {file_path_from} \n' \
                    f'to {file_path_to}')
                method(file_path_from, file_path_to)
            return copy_method2
        self.copy_method = decorate_copy(copy_method)

        def decorate_del(method):
            def del_method2(file_path_from):
                print(f'delete file {file_path_from}')
                method(file_path_from)
            return del_method2
        self.del_method = decorate_del(del_method)

        if self.path_from == self.path_to:
            print(f'from- and to-directory are the same: {self.path_from}. \n' \
                'The transporter do nothing. Do you want to continue?')
            if not self.respond_yes():
                raise UserCancelException()

        for path_use in [self.path_from, self.path_to]:
            self.check_path(path_use)
        
        if confirm:
            print('The file will be moved \n' \
                f'from {self.path_from} \n' \
                f'to {self.path_to} \n' \
                'each time the method "transport" is called with a filename.')
            print('Are you sure?')
            if not self.respond_yes():
                raise UserCancelException()
        
        if threading:
            self.executor = ThreadPoolExecutor(max_workers=1)
        else:
            self.executor = DummyExecutor()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.executor.__exit__(exc_type, exc_val, exc_tb)
        return False
    
    def shutdown(self, *args, **kwargs):
        self.executor.shutdown(*args, **kwargs)
    
    def respond_yes(self):
        response = input('[y/n]:')
        while response not in ['y', 'n']:
            response = input('[y/n]:')
        return response == 'y'
    
    def check_path(self, path_use):
        if not path_use.exists():
            print(f'The directory {path_use} does not exist. Do you want to make it?')
            if self.respond_yes():
                path_use.mkdir(parents=True)
            else:
                raise UserCancelException()
        elif path_use.is_file():
            raise NotADirectoryError(path_use)

    def transport(self, file_name):
        file_path_from = self.path_from / file_name
        file_path_to = self.path_to / file_name

        self.executor.submit(self.copy_method, file_path_from, file_path_to)
        self.executor.submit(self.del_method, file_path_from)

