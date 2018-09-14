import wx

from Frames.MoveMe.Canvas.soundBoardSubWindow import SoundBoardSubWindow
from Frames.NotesBoardPanel import generate_left_notes_panel
from bin.plugin import PluginType
from bin.soundGeneration import SoundGenerator


def generate_soundboard_panel(parent, boardType, soundGenerator):
    s = wx.BoxSizer(wx.VERTICAL)
    soundBoardPanel = SoundBoardSubWindow(parent, boardType, soundGenerator)
    s.Add(soundBoardPanel)
    return soundBoardPanel


def generate_soundboard_wrapper(parent):
    win = wx.MDIChildFrame(parent, -1, "Sounds", size=(1100, 600), pos=(272, 0),
                           style=wx.CLOSE_BOX | wx.CAPTION | wx.CLIP_CHILDREN | wx.RESIZE_BORDER)
    s = wx.BoxSizer(wx.VERTICAL)
    sound_board_panel = SoundBoardWrapper(win)
    s.Add(sound_board_panel)

    return sound_board_panel, sound_board_panel.soundboard_panel, sound_board_panel.filters_panel\
        , sound_board_panel.soundboard_notes_panel, sound_board_panel.soundboard_filters_notes_panel


class SoundBoardWrapper(wx.Panel):
    def __init__(self, parent):
        self.frameParent = None
        self.associationData = {}
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self.soundGenerator = SoundGenerator()

        self.soundBoardText = wx.StaticText(self, -1, "Notes")
        self.filtersText = wx.StaticText(self, -1, "Filters")
        self.soundboard_panel = generate_soundboard_panel(self, PluginType.SOUNDGENERATOR, self.soundGenerator)
        self.soundboard_notes_panel = generate_left_notes_panel(self, PluginType.SOUNDGENERATOR)
        self.filters_panel = generate_soundboard_panel(self, PluginType.FILTER, self.soundGenerator)
        self.soundboard_filters_notes_panel = generate_left_notes_panel(self, PluginType.FILTER)

        self.Bind(wx.EVT_CHAR_HOOK, self.on_char)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        notes_sizer_wrapper = wx.BoxSizer(wx.HORIZONTAL)
        filters_sizer_wrapper = wx.BoxSizer(wx.HORIZONTAL)

        notes_sizer_wrapper.Add(self.soundboard_notes_panel, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT)
        notes_sizer_wrapper.Add(self.soundboard_panel, 1, wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT)

        filters_sizer_wrapper.Add(self.soundboard_filters_notes_panel, 0, wx.EXPAND | wx.ALL)
        filters_sizer_wrapper.Add(self.filters_panel, 1, wx.EXPAND | wx.ALL)

        vertical_sizer_wrapper = wx.BoxSizer(wx.VERTICAL)
        vertical_sizer_wrapper.Add(self.soundBoardText, 0, wx.EXPAND)
        vertical_sizer_wrapper.Add(notes_sizer_wrapper, 6, wx.EXPAND)
        vertical_sizer_wrapper.Add(self.filtersText, 0, wx.EXPAND)
        vertical_sizer_wrapper.Add(filters_sizer_wrapper, 1, wx.EXPAND)

        self.SetSizer(vertical_sizer_wrapper)

    def on_char(self, event):
        self.soundboard_panel.on_char(event)
        self.filters_panel.on_char(event)
        event.Skip()

    def OnClose(self, evt):
        evt.Veto()