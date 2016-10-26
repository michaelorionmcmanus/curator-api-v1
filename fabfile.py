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

# def debugsls(cmd):
#     local('node --debug-brk=5858 ' + npm_modules + '/serverless/bin/serverless ' + cmd)

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
    virtual_env_bin = local('echo $VIRTUAL_ENV', capture=True)
    with open('.vscode/launch.json') as data_file:
        launch_data = json.load(data_file)
    rootDir = 'app/functions'
    functions = []

    gen_code = {
        "name": 'Generate launch config',
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
            "generate_vscode_launch_file"
        ]
    }

    # Meta!
    functions.append(gen_code)
    rebuild_db = {
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
    functions.append(rebuild_db)

    for dirName, subdirList, fileList in os.walk(rootDir):
        # print('Found directory: %s' % dirName)
        if('event.json' and 'handler.py' in fileList):
            out = {
                "name": re.search(rootDir + '/(.*)', dirName).group(1),
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
                    "debug_func:" + dirName
                ]
            }
            functions.append(out)
    
    launch_data['configurations'] = functions 

    with open('.vscode/launch.json', 'w') as data_file:
        data_file.write(json.dumps(launch_data))

# load all db models and generate schema. Run this after deleting the local database.
def rebuild_database():
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
    engine.create_schema()
    tables = [table for table in engine.dynamo.list_tables()]
    print "This engine has the following tables " + str(tables)
    for table in tables:
        engine.dynamo.describe_table(table)

def debug_func(function_dir, aws_profile="default"):
    #TODO: This should be overridable 
    os.environ['USE_LOCAL_DB'] = 'True'
    # Get the function path.
    function_path = function_dir + '/handler.py'
    # Get event test event data.
    with open(function_dir + '/event.json') as data_file:
        event_data = json.load(data_file)
    # Load environment vars
    load(aws_profile=aws_profile)
    # Load the handler as a module.
    module = imp.load_source('handler', function_path)
    result = module.handler(event_data, None)
    
    print(json.dumps(result, indent=2, sort_keys=True))