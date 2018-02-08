import wx

from Frames.MoveMe.Canvas.soundBoard import SoundBoard


def generate_soundboard_panel(parent):
    win = wx.MDIChildFrame(parent, -1, "Sounds", size=(1100, 600), pos=(272, 0),
                           style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    soundBoardPanel = SoundBoard(win)
    s.Add(soundBoardPanel)
    return soundBoardPanel
