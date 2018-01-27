import wx

def generate_plugins_frame(parent):
    win = wx.MDIChildFrame(parent, -1, "Plugins", size=(110,600), pos=(0,0), style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    win.SetSizeHints(110,600, 1200, 1200)
    win.Show(True)

