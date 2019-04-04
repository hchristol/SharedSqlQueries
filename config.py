from builtins import object
__author__ = 'hchristol'

#json config file utility

from codecs import open  # required for utf8 json encoding
from qgis.core import *
import os
import json  # required for json config file reading


# return value from a key. key can be an array to dive into json tree values
def value(dico, cle, NoneValue=""):

    if cle is None:
        return None

    #array : dive into tree
    if isinstance(cle, list):
        if len(cle) == 0:
            return None
        if len(cle) == 1:
            return value(dico, cle[0], NoneValue) #no more than one key : return its only one value

        return value(value(dico, cle[0], NoneValue), cle[1:], NoneValue) #recursive return

    #cle is a string : return its value
    if cle not in dico:
        return None
    if NoneValue is not None:
        if dico[cle] == NoneValue:
            return None
    return dico[cle]


class JsonFile(object):

    def __init__(self, directoryPath=None):
        # load config file
        if directoryPath is None:
            directoryPath = os.path.dirname(__file__) + '/config.json'

        self.config = json.loads(open(directoryPath, 'r', "utf8").read())

    def value(self, cle, NoneValue=None):
        return value(self.config, cle, NoneValue)

    def true_false_value(self, cle, NoneValue=None):
        v=value(self.config, cle, NoneValue)
        if v is None:
            return False
        if isinstance(v, str) or isinstance(v, str):
            return v.lower() == "true"
        return False
