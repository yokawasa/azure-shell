# -*- coding: utf-8 -*- 

import os
import sys
import re
import subprocess

from .cache import AzureShellCache

def _ERR(s):
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
