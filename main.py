import wx
from toolbarHelper import *
from windowsHelper import *
from Frames.plugins_panel import *
from Frames.instruments_panel import *
from Frames.soundboard_panel import *


class MDIFrame(wx.MDIParentFrame):
    def __init__(self):
        wx.MDIParentFrame.__init__(self, None, -1, "PyMusicMaker", size=(1400, 800))
        menu = wx.Menu()
        menu.Append(5001, "&Exit")
        menubar = wx.MenuBar()
        menubar.Append(menu, "&File")

        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_exit, id=5001)

        play_menu = PlayMenu(self)
        instrumentsPanel = generate_instruments_panel(self)
        pluginsPanel = generate_plugins_panel(self, instrumentsPanel)
        soundBoardPanel = generate_soundboard_panel(self, instrumentsPanel)

        play_menu.bind_play_button(soundBoardPanel.on_play)

        #generate_keyboard_window(self)

    def on_exit(self, evt):
        self.Close(True)

app = wx.App()
frame = MDIFrame()
frame.Show()
app.MainLoop()