#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import pypandoc

f = open('README.txt','w+', encoding='utf-8')
f.write(pypandoc.convert('README.md', 'rst'))
f.close()
os.system("python setup.py egg_info")
os.remove('README.txt')
