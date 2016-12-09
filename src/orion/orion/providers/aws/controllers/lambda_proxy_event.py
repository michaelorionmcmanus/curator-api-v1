class LambdaProxyController():
    def __init__(self):
        self.methods = {}

    def get(self, func, *args, **kwargs):
        self.methods['GET'] = func

    def post(self, func, *args, **kwargs):
        self.methods['POST'] = func

    def method(self, *args, **kwargs):
        pass

    def run(self, *args, **kwargs):
        event = args[0]
        context = args[1]
        method = event['httpMethod']
        method_handler = self.methods[method]
        return method_handler(event, context)

LambdaProxySingleton = LambdaProxyController()

def get(*args, **kwargs):
    return LambdaProxySingleton.get(*args, **kwargs)

def post(*args, **kwargs):
    return LambdaProxySingleton.post(*args, **kwargs)

def handler(*args, **kwargs):
    return LambdaProxySingleton.run(*args, **kwargs)