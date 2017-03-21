# -*- coding: utf-8 -*- 

import os
import sys
import re
import subprocess

from .cache import AzureShellCache

AZURE_SHELL_MINIMUM_AZURE_CLI_VERSION = '2.0.0'

def AS_ERR(s):
    sys.stderr.write("{}\n".format(s))

def find_executable_path(executable):
    path = os.environ['PATH']
    pathlist = path.split(os.pathsep)
    if os.path.isfile(executable):
        return executable
    else:
        for path in pathlist:
            f = os.path.join(path, executable)
            if os.path.isfile(f):
                return f
    return ''

def get_cli_version():
    v = AzureShellCache.Instance().get('azure_cli_version')
    if v:
        return v
    cmd_string = 'az --version'
    proc = subprocess.Popen(cmd_string,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = proc.stdout.readline()
        l = line.strip()  
        if l.startswith('azure-cli'):
            r = re.compile("([a-z-]*) \((.*)\)")
            o = r.findall(l)
            if len(o) == 1 and len(o[0]) ==2:
                v = o[0][1]
                AzureShellCache.Instance().set('azure_cli_version',v)
                break
        if not line and proc.poll() is not None:
            break
    return v


def get_azurecli_modules_path():
    ## Getting a path for python executable taht AzureCLI leverage
    executable = find_executable_path('az')
    python_path = None
    f = open(executable)
    l = f.readline().strip()
    while l:
        if not l.startswith('#') and l.find('python'):
            cols = l.split()
            if len(cols) > 1:
                python_path = cols[0]
                break
        l = f.readline().strip()
    f.close
    if not python_path:
        return None 
    ## Getting python module paths that Azure CLI configures
    azurecli_modules_path =None
    cmd_string="{} <<EOF\nimport sys\nprint ' '.join(sys.path)\nEOF".format(python_path)
    proc = subprocess.Popen(cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    azureclicore= 'azure/cli/core'
    while True:
        l = proc.stdout.readline().strip()
        if l:
            paths = l.split()
            for path in paths:
                d = os.path.join(path, azureclicore)
                if os.path.exists(d):
                    azurecli_modules_path = path 
                    break
        if not l and proc.poll() is not None:
            break
    return azurecli_modules_path
