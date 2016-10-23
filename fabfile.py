from fabric.api import local
import time
import os
from fabric.context_managers import lcd
import json
import imp
import re
from app.shared.util.load_env import load

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

    for dirName, subdirList, fileList in os.walk(rootDir):
        # print('Found directory: %s' % dirName)
        if('event.json' and 'handler.py' in fileList):
            out = {
                "name": dirName,
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
    

def debug_func(function_dir, aws_profile="default"):
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