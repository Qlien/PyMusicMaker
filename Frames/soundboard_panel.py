import wx

from Frames.MoveMe.Canvas.soundBoardSubWindow import SoundBoardSubWindow
from Frames.filters_panel import generate_filters_panel


def generate_soundboard_panel(parent, boardType):
    s = wx.BoxSizer(wx.VERTICAL)
    soundBoardPanel = SoundBoardSubWindow(parent, boardType)
    s.Add(soundBoardPanel)
    return soundBoardPanel


def generate_soundboard_wrapper(parent):
    win = wx.MDIChildFrame(parent, -1, "Sounds", size=(1100, 600), pos=(272, 0),
                           style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    sound_board_panel = SoundBoardWrapper(win)
    s.Add(sound_board_panel)

    return sound_board_panel, sound_board_panel.soundboard_panel, sound_board_panel.filters_panel


class SoundBoardWrapper(wx.Panel):
    def __init__(self, parent):

        self.frameParent = None
        self.associationData = {}
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self.soundBoardText = wx.StaticText(self, -1, "Notes")
        self.filtersText = wx.StaticText(self, -1, "Filters")
        self.soundboard_panel = generate_soundboard_panel(self, "notes")
        self.filters_panel = generate_soundboard_panel(self, "filters")

        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.soundBoardText, 0, wx.EXPAND)
        s.Add(self.soundboard_panel, 6, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT)
        s.Add(self.filtersText, 0, wx.EXPAND)
        s.Add(self.filters_panel, 1, wx.EXPAND | wx.ALL)
        self.SetSizer(s)
