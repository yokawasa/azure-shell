# -*- coding: utf-8 -*-

class AzureShellCache:

    __inst = None
    __cache = {}

    @staticmethod
    def Instance():
        if AzureShellCache.__inst == None:
            AzureShellCache()
        return AzureShellCache.__inst

    def __init__(self):
        if AzureShellCache.__inst != None:
            raise Exception("This must not be called!!")
        AzureShellCache.__inst = self

    def set(self, k, v):
        self.__cache[k] = v

    def get(self, k):
        return self.__cache.get(k)
