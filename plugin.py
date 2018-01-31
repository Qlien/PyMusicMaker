from enum import Enum
import wx


class PluginBase(object):
    def __init__(self, type, icon):
        self.icon = icon
        self.pluginType = type
        self.iconSize = (100,50)


class PluginType(Enum):
    SOUNDGENERATOR = 1
    FILTER = 2