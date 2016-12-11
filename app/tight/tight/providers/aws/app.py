import os, importlib, traceback, sys
from functools import partial
from tight.core.logger import info

def run():
    try:
        info(message='CREATING APP')
        create(sys.modules['app_index'])
    except Exception as e:
        info(message='UNABLE TO RUN')
        info(message=e)
        traceback.print_exc()

def create(current_module):
    controllers = []
    for dirName, subdirList, fileList in os.walk('app/functions'):
        if ('handler.py' in fileList):
            controller_module_path = (dirName + '/handler').replace('/', '.')
            controller_name = controller_module_path.split('.')[-2]
            callback = {}
            callback[controller_name] = controller_module_path
            controllers.append(callback)

    for item in controllers:
        name, controller_module_path = item.popitem()
        def function(*args, **kwargs):
            controller_module_path = args[0]
            func_args = args[1:4]
            callback = importlib.import_module(controller_module_path, 'handler')
            return callback.handler(*func_args, **kwargs)

        bound_function = partial(function, *(controller_module_path, name))
        function.__name__ = name + '_module'
        setattr(current_module, name, bound_function)