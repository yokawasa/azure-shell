#!/usr/bin/env python
import re
import ast

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

requires = [
    'prompt-toolkit>=1.0.0,<1.1.0',
    'configparser>=3.5.0',
    'Pygments>=2.1.3,<3.0.0',
    'pyyaml',
]

with open('azureshell/__init__.py', 'r') as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        fd.read(), re.MULTILINE).group(1)

setup(
    description='An interactive Azure CLI 2.0 command line interface',
    long_description=long_description,
    author='Yoichi Kawasaki',
    author_email='yoichi.kawasaki@outlook.com',
    name='azure-shell',
    version=version,
    url='https://github.com/yokawasa/azure-shell',
    download_url='https://pypi.python.org/pypi/azure-shell',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    package_data={'azureshell': ['azureshell.conf']},
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'azure-shell = azureshell:main',
            'azure-shell-index-generator = azureshell.index_generator:main',
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
