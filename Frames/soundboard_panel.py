import wx, sys, os
from Frames.MoveMe.Canvas.Canvas import Canvas

def generate_soundboard_panel(parent, instrumentsPanel):
    win = wx.MDIChildFrame(parent, -1, "Sounds", size=(1100,600), pos=(272,0), style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    soundBoardPanel = Canvas(win, instrumentsPanel)
    s.Add(soundBoardPanel)
    return soundBoardPanel
