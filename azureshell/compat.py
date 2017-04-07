# -*- coding: utf-8 -*- 

import sys

if sys.version_info[0] == 3:
    ## Python3
    text_type = str
    import urllib.request as urllib2
    import configparser
else:
    ## Python2
    text_type = unicode
    import urllib2
    import ConfigParser as configparser
