# azure-shell 

An interactive Azure CLI 2.0 command line interface

![]((https://github.com/yokawasa/azure-shell/raw/master/img/azure-shell-console.gif)) 

## Supported Environments

* Python versions: 2.7, 3.3, 3.4, 3.5, 3.5 and maybe more
* OS: Mac, Ubuntu, CentOS, Bash-on-Windows, or any platform where azure-cli can be installed

## Installation

The azure-shell requires python and pip to install. You can install the azure-shell using pip:

```
pip install azure-shell
```

If you've already have azure-shell installed and want to upgrade to the latest version, you can upgrade like this:

```
pip install --upgrade azure-shell
```

Once you've installed the azure-shell, you can run azure-shell now:

```
azure-shell
```

## Configuration

You can basically run without making any configurations by default but you can give options to azure-shell to configure:

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


## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/yokawasa/azure-shell

## More Information

* [Get started with Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/get-started-with-azure-cli)
* [Install Azure CLI 2.0](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

