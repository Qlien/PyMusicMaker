from bin.frame import MainWindowFrame
from bin.toolbarHelper import *


class App(object):
    def __init__(self):

        self.app = wx.App()
        self.frame = MainWindowFrame(None, -1, "PyMusicMaker", size=(1400, 800))
        self.start()

    def start(self):

        self.frame.Show()
        self.app.MainLoop()


app = App()
app.start()
