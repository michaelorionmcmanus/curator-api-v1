import os, importlib, inspect
from functools import partial
def create(current_module):
    controllers = []
    for dirName, subdirList, fileList in os.walk('src/functions'):
        if ('handler.py' in fileList):
            controller_module_path = (dirName + '/handler').replace('/', '.')
            controller_name = controller_module_path.split('.')[-2]
            controller_module = importlib.import_module(controller_module_path, 'handler')
            handler = controller_module.handler
            callback = {}
            callback[controller_name] = handler
            controllers.append(callback)

    for item in controllers:
        name, callback = item.popitem()
        def function(*args, **kwargs):
            callback = args[0]
            func_args = args[1:4]
            return callback(*func_args, **kwargs)

        bound_function = partial(function, *(callback, name))
        function.__name__ = name + '_module'
        setattr(current_module, name, bound_function)