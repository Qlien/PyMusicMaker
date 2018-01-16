import wx
from toolbarHelper import *


class MDIFrame(wx.MDIParentFrame):
    def __init__(self):
        wx.MDIParentFrame.__init__(self, None, -1, "PyMusicMaker", size=(1200, 800))
        menu = wx.Menu()
        menu.Append(5000, "&New Window")
        menu.Append(5001, "&Exit")
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnNewWindow, id=5000)
        self.Bind(wx.EVT_MENU, self.OnExit, id=5001)

        generate_play_menu_toolbar(self, self.OnExit, self.OnExit, self.OnExit, self.OnExit)

    def OnExit(self, evt):
        self.Close(True)

    def OnNewWindow(self, evt):
        win = wx.MDIChildFrame(self, -1, "Child Window", style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
        win.Show(True)

def scaleImage(imageDir, width, height, quality = wx.IMAGE_QUALITY_HIGH):
    return wx.Bitmap(wx.Bitmap(imageDir).ConvertToImage().Scale(width, height, wx.IMAGE_QUALITY_HIGH))

app = wx.App()
frame = MDIFrame()
frame.Show()
app.MainLoop()