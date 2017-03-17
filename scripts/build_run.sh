#!/bin/sh

cwd=`dirname "$0"`
expr "$0" : "/.*" > /dev/null || cwd=`(cd "$cwd" && pwd)`
cd ${cwd}/..
sudo rm -rf dist build
python setup.py sdist
sudo python setup.py install
cd ${cwd}
azure-shell
