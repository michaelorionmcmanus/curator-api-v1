from fabric.api import local
import glob
import time
import os
import sys
from os.path import dirname, basename, isfile, join
from dotenv import load_dotenv
from fabric.context_managers import lcd
import json
import imp
import re
from src.shared.util.load_env import load
from flywheel import Model, Field, Engine
import yaml
import pytest
from dynamo3 import DynamoDBConnection
from collections import namedtuple

# def debugsls(cmd):
#     local('node --debug-brk=5858 ' + npm_modules + '/serverless/bin/serverless ' + cmd)

virtual_env_bin = local('echo $VIRTUAL_ENV', capture=True)

DEFAULT_LAUNCH_ITEM = {
        "name": 'rebuild database',
        "type": "python",
        "request": "launch",
        "stopOnEntry": False,
        "pythonPath": "${config.python.pythonPath}",
        "cwd": "${workspaceRoot}",
        "program": virtual_env_bin + "/bin/fab",
        "debugOptions": [
            "WaitOnAbnormalExit",
            "WaitOnNormalExit",
            "RedirectOutput"
        ],
        "args": [
            "rebuild_database"
        ]
    }

# Auto generate env file if not present.
if not os.path.isfile('./src/.env.yml'):
    dist_env_vars = yaml.load(open('./src/.env.dist.yml'))
    for k, v in dist_env_vars.iteritems():
        if os.environ.get(k):
            dist_env_vars[k] = os.environ[k]
    stream = file('./src/.env.yml', 'w')
    yaml.safe_dump(dist_env_vars, stream)
    print yaml.dump(dist_env_vars)

env_vars = yaml.load(open('./src/.env.yml'))
for k, v in env_vars.iteritems():
    os.environ[k] = v

def debugsls(cmd):
    local('node --debug-brk=5858 $NVM_BIN/serverless ' + cmd)

def pip_install_dep(lib):
    local('pip install -t src/vendored/ ' + lib + ' --upgrade')

def pip_uninstall_dep(lib):
    local('pip uninstall -t src/vendored/ ' + lib)

def pip_freeze_vendor():
    packages = []
    for dirName, subdirList, fileList in os.walk('src/vendored'):
        if('METADATA' in fileList):
            with open(dirName + '/METADATA') as data_file:
                for line in data_file:
                    versionMatch = re.match('^Version: (.*)$', line)
                    if(versionMatch):
                        version = versionMatch.group(1)
                    nameMatch = re.match('^Name: (.*)$', line)
                    if(nameMatch):
                        name = nameMatch.group(1)
            packages.append(name + '==' + version)
    
    with open('./vendor-requirements.txt', 'w') as data_file:
        data_file.write('\r'.join(packages))

def pip_install_vendor_deps():
    local('pip install -t src/vendored -r vendor-requirements.txt')
def test(test=None):
    os.environ['USE_LOCAL_DB'] = 'True'
    if test:
        pytest.main([test])
        # local('py.test {} --confcutdir ./'.format(test))
    else:
        local('py.test tests --confcutdir ./')

def generate_vscode_launch_file():
    with open('.vscode/launch.json') as data_file:
        launch_data = json.load(data_file)
    rootDir = 'src/functions'
    functions = []

    gen_code = DEFAULT_LAUNCH_ITEM.copy()
    gen_code['name'] = 'Generate launch config'
    gen_code['args'] = ['generate_vscode_launch_file']

    rebuild_db = DEFAULT_LAUNCH_ITEM.copy()
    rebuild_db['name'] = 'rebuild database'
    rebuild_db['args'] = ['rebuild_database']

    generate_cf_dynamo_schema = DEFAULT_LAUNCH_ITEM.copy()
    generate_cf_dynamo_schema['name'] = 'generate CF compatible DynamoDB schema'
    generate_cf_dynamo_schema['args'] = ['generate_cf_dynamo_schema']

    functions.append(rebuild_db)
    functions.append(gen_code)
    functions.append(generate_cf_dynamo_schema)

    for dirName, subdirList, fileList in os.walk(rootDir):
        # print('Found directory: %s' % dirName)
        if('event.json' and 'handler.py' in fileList):
            for item in ['GET', 'POST', 'PATCH', 'DELETE', 'UNIT_TESTS', 'INTEGRATION_TESTS']:
                out = DEFAULT_LAUNCH_ITEM.copy()
                out['name'] = re.search(rootDir + '/(.*)', dirName).group(1) + ' %s' % item
                if item == 'UNIT_TESTS':
                    function_name = dirName.split('/')[-1]
                    out['args'] = ['test:' + 'tests/functions/{}/{}_unit_test.py'.format(function_name, function_name) ]
                elif item == 'INTEGRATION_TESTS':
                    function_name = dirName.split('/')[-1]
                    out['args'] = ['test:' + 'tests/functions/{}/{}_integration_test.py'.format(function_name, function_name) ]
                else:
                    out['args'] = ['debug_func:' + dirName + ',' + item]
                functions.append(out)
    
    launch_data['configurations'] = functions 

    with open('.vscode/launch.json', 'w') as data_file:
        data_file.write(json.dumps(launch_data))

def _init_db():
    engine = Engine()
    # connect to local db
    engine.connect('us-west-2', host='localhost',
        port=8000,
        access_key='anything',
        secret_key='anything',
        is_secure=False)
    # load models
    sys.path = ['./src/models'] + sys.path
    modelModules = glob.glob('./src/models'+"/*.py")
    models = [ basename(f)[:-3] for f in modelModules if isfile(f)]
    for modelName in models:
        if modelName != '__init__':
            engine.register(getattr(__import__(modelName), modelName))
    return engine

# load all db models and generate schema. Run this after deleting the local database.
def rebuild_database():
    engine = _init_db()
    engine.create_schema()
    tables = [table for table in engine.dynamo.list_tables()]
    print "This engine has the following tables " + str(tables)
    for table in tables:
        engine.dynamo.describe_table(table)

def debug_func(function_dir, method):
    profile = os.environ['AWS_DEFAULT_PROFILE']
    #TODO: This should be overridable
    os.environ['USE_LOCAL_DB'] = 'True'
    # Get the function path.
    function_path = function_dir + '/handler.py'
    function_package = (function_dir + '/handler').replace('/', '.')
    with open('base-event.yml') as data_file:
        base_event = yaml.load(data_file)

    with open(function_dir + '/events.yml') as data_file:
        event_data = yaml.load(data_file)['methods'][method]
    
    base_event['httpMethod'] = method

    if not (event_data['body'] == None):
        base_event['body'] = json.dumps(event_data['body'])
    if('pathParameters' in event_data):
        base_event['pathParameters'] = event_data['pathParameters']
    if('queryStringParameters' in event_data):
        base_event['queryStringParameters'] = event_data['queryStringParameters']
    # Load environment vars
    load(aws_profile=profile)
    # Load the handler as a module.
    # module = __import__(function_package, fromlist=[''])
    module = imp.load_source('handler', function_path)
    result = module.handler(base_event, None, None)
    is_json = True
    if 'Content-Type' in result['headers']:
        if result['headers']['Content-Type'] == 'text/plain':
            is_json = False
    if is_json:
        result['body'] = json.loads(result['body'])
    print(json.dumps(result, indent=2, sort_keys=True))

def generate_base_event():
    with open('./sample-event.json') as data_file:
        base_event = json.loads(data_file.read())

    stream = file('./base-event.yml', 'w')
    yaml.safe_dump(base_event, stream)

def write_schema_to_yaml(**kwargs):
    properties = kwargs.copy()
    table_name = "-".join(kwargs.pop('TableName').split('-')[3:])
    properties['TableName'] = '${{self:service}}-${{opt:stage, self:provider.stage}}-%s' % table_name
    table = {
        'Type': 'AWS::DynamoDB::Table',
        'Properties': properties
    }
    stream = file('./schemas/dynamo/{}.yml'
                  .format(table_name), 'w')
    yaml.safe_dump(table, stream)

def generate_cf_dynamo_schema():
    dynamo_connection = DynamoDBConnection()
    class FakeClient(object):
        def create_table(self, *args, **kwargs):
            write_schema_to_yaml(**kwargs)
            return {}

    client = FakeClient()
    dynamo_connection.client = client

    class FakeDynamo(object):
        def list_tables(self):
            return []
        def create_table(self, *args):
            result = dynamo_connection.create_table(*args)
        def describe_table(self, *args):
            StatusStruct = namedtuple('Status', 'status')
            return StatusStruct(status='ACTIVE')

    dynamo = FakeDynamo()
    engine = Engine()
    engine.dynamo = dynamo

    sys.path = ['./src/models'] + sys.path
    modelModules = glob.glob('./src/models'+"/*.py")
    models = [ basename(f)[:-3] for f in modelModules if isfile(f)]
    for modelName in models:
        if modelName != '__init__':
            engine.register(getattr(__import__(modelName), modelName))

    engine.create_schema()