from fabric.api import local
import glob
import time
import os
import sys
from os.path import dirname, basename, isfile
from fabric.context_managers import lcd
import json
import imp
import re
from app.shared.util.load_env import load
from flywheel import Model, Field, Engine
import yaml

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

def debugsls(cmd):
    local('node --debug-brk=5858 $NVM_BIN/serverless ' + cmd)

def pip_install_dep(lib):
    local('pip install -t app/vendored/ ' + lib + ' --upgrade')

def pip_uninstall_dep(lib):
    local('pip uninstall -t app/vendored/ ' + lib)

def pip_freeze_vendor():
    packages = []
    for dirName, subdirList, fileList in os.walk('app/vendored'):
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
    local('pip install -t app/vendored -r vendor-requirements.txt')                 
def test():
    local('py.test tests --confcutdir ./')

def generate_vscode_launch_file():
    with open('.vscode/launch.json') as data_file:
        launch_data = json.load(data_file)
    rootDir = 'app/functions'
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
            for item in ['GET', 'POST', 'PATCH', 'DELETE']:
                out = DEFAULT_LAUNCH_ITEM.copy()
                out['name'] = re.search(rootDir + '/(.*)', dirName).group(1) + ' %s' % item
                out['args'] = ['debug_func:' + dirName + ',' + item] 
                functions.append(out)
    
    launch_data['configurations'] = functions 

    with open('.vscode/launch.json', 'w') as data_file:
        data_file.write(json.dumps(launch_data))

def _init_db():
    sys.path = ['./app/models'] + sys.path
    engine = Engine()
    # connect to local db
    engine.connect('us-west-2', host='localhost',
        port=8000,
        access_key='anything',
        secret_key='anything',
        is_secure=False)
    # load models
    modelModules = glob.glob('./app/models'+"/*.py")
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
    with open('base-event.yml') as data_file:
        base_event = yaml.load(data_file)

    with open(function_dir + '/events.yml') as data_file:
        event_data = yaml.load(data_file)['methods'][method]
    
    base_event['httpMethod'] = method
    base_event['body'] = json.dumps(event_data['body'])
    base_event['pathParameters'] = json.dumps(event_data['pathParameters'])
    # Load environment vars
    load(aws_profile=profile)
    # Load the handler as a module.
    module = imp.load_source('handler', function_path)
    result = module.handler(base_event, None)
    result['body'] = json.loads(result['body'])
    print(json.dumps(result, indent=2, sort_keys=True))

def generate_base_event():
    with open('./sample-event.json') as data_file:
        base_event = json.loads(data_file.read())

    stream = file('./base-event.yml', 'w')
    yaml.safe_dump(base_event, stream)


def generate_cf_dynamo_schema():
    engine = _init_db()
    tables = [table for table in engine.dynamo.list_tables()]
    for table in tables:
        response = engine.dynamo.describe_table(table).response
        table_name = "-".join(response['TableName'].split('-')[3:])
        properties = {
            'Type': 'AWS::DynamoDB::Table',
            'Properties': {
                'TableName': '${{self:service}}-${{opt:stage, self:provider.stage}}-%s' % table_name,
                'AttributeDefinitions': response['AttributeDefinitions'],
                'KeySchema': response['KeySchema'],
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': response['ProvisionedThroughput']['ReadCapacityUnits'],
                    'WriteCapacityUnits': response['ProvisionedThroughput']['WriteCapacityUnits']
                },
                'LocalSecondaryIndexes': [{'KeySchema': item['KeySchema'], 'IndexName': item['IndexName'], 'Projection': item['Projection']} for item in response['LocalSecondaryIndexes']] if 'LocalSecondaryIndexes' in response else None
            }
        }

        if(not properties['Properties']['LocalSecondaryIndexes']):
            properties['Properties'].pop('LocalSecondaryIndexes', None)

        stream = file('./schemas/dynamo/{}.yml'
            .format(table_name), 'w')
        yaml.safe_dump(properties, stream)