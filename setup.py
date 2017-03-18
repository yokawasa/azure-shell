#!/usr/bin/env python
import re
import ast

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

requires = [
    'prompt-toolkit>=1.0.0,<1.1.0',
    'configparser>=3.5.0',
    'Pygments>=2.1.3,<3.0.0',
]

with open('azureshell/__init__.py', 'r') as f:
    version = str(
        ast.literal_eval(
            re.search(
                r'__version__\s+=\s+(.*)',
                f.read()).group(1)))

setup(
    name='azure-shell',
    version=version,
    description='An interactive Azure CLI 2.0 command line interface',
    long_description=open('README.md').read(),
    author='Yoichi Kawasaki',
    url='https://github.com/yokawasa/azure-shell',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    package_data={'azureshell': ['azureshell.conf']},
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'azure-shell = azureshell:main'
        ]
    },
    license="Apache License 2.0",
    platforms='any',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='azure azure-shell, shell, azure-cli',
)
