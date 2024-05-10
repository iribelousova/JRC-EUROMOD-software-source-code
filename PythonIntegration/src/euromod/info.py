import clr as clr
import os
from utils._paths import CWD_PATH, DLL_PATH
clr.AddReference(os.path.join(DLL_PATH, "EM_XmlHandler.dll" ))
from EM_XmlHandler import CountryInfoHandler


def getInfoInString(info):
    return CountryInfoHandler.GetInfoInString(info)

class Info:
    def __init__(self,info):
        self.info = info

    def __repr__(self):  
        return (getInfoInString(self.info))

    def __getitem__(self,key):
        return self.info[key]
