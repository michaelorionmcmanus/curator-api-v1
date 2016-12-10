import sys, importlib, json, traceback
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
        controller_name = func.func_globals['__package__'].split('.')[-1]
        self.methods['{}:GET'.format(controller_name)] = func

    def post(self, func, *args, **kwargs):
        self.attach_handler(func)
        controller_name = func.func_globals['__package__'].split('.')[-1]
        self.methods['{}:POST'.format(controller_name)] = func

    def patch(self, func, *args, **kwargs):
        self.attach_handler(func)
        controller_name = func.func_globals['__package__'].split('.')[-1]
        self.methods['{}:PATCH'.format(controller_name)] = func

    def put(self, func, *args, **kwargs):
        self.attach_handler(func)
        controller_name = func.func_globals['__package__'].split('.')[-1]
        self.methods['{}:PUT'.format(controller_name)] = func

    def delete(self, func, *args, **kwargs):
        self.attach_handler(func)
        controller_name = func.func_globals['__package__'].split('.')[-1]
        self.methods['{}:DELETE'.format(controller_name)] = func

    def options(self, func, *args, **kwargs):
        self.attach_handler(func)
        controller_name = func.func_globals['__package__'].split('.')[-1]
        self.methods['{}:OPTIONS'.format(controller_name)] = func

    def prepare_args(self, *args, **kwargs):
        event = args[1]
        context = args[2]
        if ('body' in event and event['body'] != None):
            try:
                event['body'] = json.loads(event['body'])
            except Exception as e:
                self.log('Could not json.loads ' + str(event['body']))
                event['body'] = {}
        try:
            principal_id = event['requestContext']['authorizer']['claims']['sub']
        except Exception as e:
            principal_id = None

        return {
            'event': event,
            'context': context,
            'principal_id': principal_id
        }

    def prepare_response(self, *args, **kwargs):
        if ('passthrough' in kwargs):
            return kwargs['passthrough']
        # Map return properties to the response.
        if ('body' not in kwargs):
            kwargs['body'] = {}
        elif (not isinstance(kwargs['body'], str)):
            kwargs['body'] = json.dumps(kwargs['body'])
        # Default response code is 200
        if ('statusCode' not in kwargs):
            kwargs['statusCode'] = 200
        # Response header needs to specify `Access-Control-Allow-Origin` in order
        # for CORS to function properly.
        if ('headers' not in kwargs):
            kwargs['headers'] = {
                'Access-Control-Allow-Origin': '*'
            }
        # Ship it!
        return kwargs

    def run(self, *args, **kwargs):
        controller_name = args[0]
        event = args[1]
        context = args[2]
        method = event['httpMethod']
        method_handler = self.methods[':'.join([controller_name, method])]
        method_handler_args = self.prepare_args(*args, **kwargs)
        method_response = method_handler(*args, **method_handler_args)
        prepared_response = self.prepare_response(**method_response)
        return prepared_response

LambdaProxySingleton = LambdaProxyController()

current_module = sys.modules[__name__]
''' Expose all method handlers'''
for method in methods:
    handler = getattr(LambdaProxySingleton, method)
    setattr(current_module, method, handler)

def handler(*args, **kwargs):
    return LambdaProxySingleton.run(*args, **kwargs)