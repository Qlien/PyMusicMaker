import wx
from plugin import PluginBase, PluginType


class Oscillator(PluginBase):
    def __init__(self):
        PluginBase.__init__(self, PluginType.SOUNDGENERATOR, wx.Bitmap('Plugins\Oscillator\Graphics\icon.png'))
        pass