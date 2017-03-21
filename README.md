# azure-shell 

An interactive Azure CLI 2.0 command line interface

![](https://github.com/yokawasa/azure-shell/raw/master/img/azure-shell-console.gif)

## Features

* Auto-completion of Azure CLI group, subgroups, commands, and parameters
* Syntax highlighting
* Command history

## Supported Environments

* Python versions: 2.7, 3.3, 3.4, 3.5, 3.5, 3.6 and maybe more
* OS: Mac, Ubuntu, CentOS, Bash-on-Windows, or any platform where azure-cli can be installed

## Prerequisites

You need Azure CLI 2.0 installed as prerequisites for azure-shell. Please refer to [Install Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) and install it if not yet installed

## Installation

The azure-shell requires python and pip to install. You can install the azure-shell using pip:

```
pip install azure-shell
```

If you've already have azure-shell installed and want to upgrade to the latest version, you can upgrade like this:

```
pip install --upgrade azure-shell
```

## Usage

Once you've installed the azure-shell, you can run azure-shell by simply typing azure-shell:

```
azure-shell
```

You can exit the azure-shell by typing either exit or quit:

```
azure> exit
```

Basically you can run azure-shell without making any configurations but you can give options to azure-shell to change its default behabior:

```
azure-shell --help

Usage: azure-shell [-h] [--version] [--basedir BASEDIR] [--config CONFIG]
                   [--index INDEX]

An interactive Azure CLI command line interface

optional arguments:
  -h, --help         show this help message and exit
  --version          show program's version number and exit
  --basedir BASEDIR  Azure Shell base dir path ($HOME/.azureshell by default)
  --config CONFIG    Azure Shell config file path
                     ($HOME/.azureshell/azureshell.conf by default)
  --index INDEX      Azure Shell index file to load ($HOME/.azureshel/cli-
                     index-<azure_cli_version>.json)
```

## Azure Shell Index Generator

You can generate an index for azure-shell using azure-shell-index-generator command. Please be noted that it will take time before all data generation works are done
 
```
azure-shell-index-generator --output ~/.azureshell/cli-index.json
```

Basically you don't need to generate the index by yourself as azure-shell automatically downloads an index from its repository and load it for commands and parameters completion in startup time. But you also can give azure-shell your index using --index option.

```
azure-shell --index ~/.azureshell/cli-index.json
```

## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/yokawasa/azure-shell

## More Information

* [Get started with Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/get-started-with-azure-cli)
* [Install Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

