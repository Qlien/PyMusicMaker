import wx, sys, os, pygame
from Frames.MoveMe.Canvas.CanvasNew import MyCanvas
from Frames.MoveMe.Canvas.Canvas import Canvas

def generate_soundboard_frame(parent):
    win = wx.MDIChildFrame(parent, -1, "Sounds", size=(1100,600), pos=(272,0), style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(Canvas(win))
