import sys, importlib
methods = [
    'get', 'post', 'patch', 'put', 'delete', 'options'
]
class LambdaProxyController():
    def __init__(self):
        self.methods = {}

    def attach_handler(self, func):
        function_package = func.func_globals['__name__']
        function_module = importlib.import_module(function_package)
        try:
            getattr(function_module, 'handler')
        except Exception as e:
            setattr(function_module, 'handler', self.run)

    def get(self, func, *args, **kwargs):
        self.attach_handler(func)
        self.methods['GET'] = func

    def post(self, func, *args, **kwargs):
        self.attach_handler(func)
        self.methods['POST'] = func

    def patch(self, func, *args, **kwargs):
        self.attach_handler(func)
        self.methods['PATCH'] = func

    def put(self, func, *args, **kwargs):
        self.attach_handler(func)
        self.methods['PUT'] = func

    def delete(self, func, *args, **kwargs):
        self.attach_handler(func)
        self.methods['DELETE'] = func

    def options(self, func, *args, **kwargs):
        self.attach_handler(func)
        self.methods['OPTIONS'] = func

    def run(self, *args, **kwargs):
        event = args[0]
        context = args[1]
        method = event['httpMethod']
        method_handler = self.methods[method]


        return method_handler(event, context)

LambdaProxySingleton = LambdaProxyController()

current_module = sys.modules[__name__]
''' Expose all method handlers'''
for method in methods:
    handler = getattr(LambdaProxySingleton, method)
    setattr(current_module, method, handler)

def handler(*args, **kwargs):
    return LambdaProxySingleton.run(*args, **kwargs)