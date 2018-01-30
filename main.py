import wx
from toolbarHelper import *
from windowsHelper import *
from Frames.plugins_tree_frame import *
from Frames.instruments_frame import *
from Frames.soundboard_frame import *


class MDIFrame(wx.MDIParentFrame):
    def __init__(self):
        wx.MDIParentFrame.__init__(self, None, -1, "PyMusicMaker", size=(1400, 800))
        menu = wx.Menu()
        menu.Append(5001, "&Exit")
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_exit, id=5001)

        generate_play_menu_toolbar(self, self.on_exit, self.on_exit, self.on_exit, self.on_exit)
        generate_plugins_frame(self)
        generate_instruments_frame(self)
        generate_soundboard_frame(self)
        #generate_keyboard_window(self)

    def on_exit(self, evt):
        self.Close(True)

app = wx.App()
frame = MDIFrame()
frame.Show()
app.MainLoop()