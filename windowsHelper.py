import wx
from toolbarHelper import *

def generate_keyboard_window(parent):
    win = wx.MDIChildFrame(parent, -1, "Keyboard", style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    win.Show(True)