import os
import wx
import Plugins


def generate_plugins_frame(parent):
    win = wx.MDIChildFrame(parent, -1, "Plugins", size=(110,600), pos=(0,0), style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(MineDrop(win, parent), 1, wx.EXPAND)
    win.SetSizer(s)
    win.SetSizeHints(110,600, 1200, 1200)
    win.Show(True)


class MyTextDropTarget(wx.TextDropTarget):
    def __init__(self, object):
        wx.TextDropTarget.__init__(self)
        self.object = object

    def OnDropText(self, x, y, data):
        self.object.InsertStringItem(0, data)


class MineDrop(wx.Panel):
    def __init__(self, parent, frameParent):
        self.frameParent = frameParent
        wx.Panel.__init__(self, parent)
        self.tree_ctrl = wx.TreeCtrl(self, -1, style=wx.TR_DEFAULT_STYLE)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.tree_ctrl, 1, wx.EXPAND)
        self.SetSizer(s)

        # Add the tree root
        root = self.tree_ctrl.AddRoot('Instruments')
        dir_path = os.getcwd()
        for path, dirs, files in os.walk(dir_path + '/Plugins'):
            print(path)
            for f in files:
                print(f)
        print(dir_path)
        self.tree_ctrl.AppendItem(root, 'Oscillator')
        image_list = wx.ImageList(100, 50)
        #OscillatorImg = image_list.Add(wx.Image("images/grooveshark (Custom).png", wx.BITMAP_TYPE_PNG).Scale(100, 50).ConvertToBitmap())
        self.tree_ctrl.ExpandAll()
        self.Centre()
        self.tree_ctrl.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragInit)
        self.tree_ctrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivated)

    def OnDragInit(self, event):
        text = self.tree_ctrl.GetItemText(event.GetItem())

        tdo = wx.TextDataObject(text)
        tds = wx.DropSource(self.tree_ctrl)
        tds.SetData(tdo)
        tds.DoDragDrop(True)


    def OnActivated(self, event):
        win = wx.MDIChildFrame(self.frameParent, -1, "Plugins",
                               style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
