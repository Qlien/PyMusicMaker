from enum import Enum
import wx


class PluginBase(wx.Panel):
    def __init__(self, frameParent, type, icon):
        self.frameParent = frameParent
        self.win = wx.MDIChildFrame(frameParent, -1, "Oscillator", size=(600,400),
                               style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)

        super(wx.Panel, self).__init__(self.win)
        icn = wx.Icon()
        icn.CopyFromBitmap(icon)
        self.win.SetIcon(icn)

        self.frameParent = frameParent
        self.icon = icon
        self.pluginType = type
        self.pluginName = "Oscillator"
        self.iconSize = (100,50)


class PluginType(Enum):
    SOUNDGENERATOR = 1
    FILTER = 2