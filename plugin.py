from enum import Enum
import wx


class PluginBase(wx.Panel):
    def __init__(self, frameParent, type, icon, name=''):
        self.frameParent = frameParent
        self.win = wx.MDIChildFrame(frameParent, -1, name, size=(600,400),
                               style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)

        super(wx.Panel, self).__init__(self.win)
        icn = wx.Icon()
        icn.CopyFromBitmap(icon)
        self.win.SetIcon(icn)

        self.frameParent = frameParent
        self.icon = icon
        self.pluginType = type
        self.pluginName = name
        self.iconSize = (100,50)

    def generateSound(self, parentWindow):
        raise NotImplementedError

    def show_window(self, show):
        self.win.Show() if show else self.win.Hide()

    def is_window_visible(self):
        return self.win.IsShown()

class PluginType(Enum):
    SOUNDGENERATOR = 1
    FILTER = 2
    SOUND = 4