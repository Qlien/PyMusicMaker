import os
import wx


def generate_plugins_frame(parent):
    win = wx.MDIChildFrame(parent, -1, "Plugins", size=(110,600), pos=(0,0), style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(MineDrop(win), 1, wx.EXPAND)
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
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.tree_ctrl = wx.TreeCtrl(self, -1, style=wx.TR_DEFAULT_STYLE)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.tree_ctrl, 1, wx.EXPAND)
        self.SetSizer(s)

        # Add the tree root
        root = self.tree_ctrl.AddRoot('Instruments')

        for i in range(10):
            self.tree_ctrl.AppendItem(root, 'Item %d' % (i + 1))

            self.tree_ctrl.ExpandAll()
        self.Centre()
        self.tree_ctrl.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragInit)

    def OnDragInit(self, event):
        my_data = wx.TextDataObject("This text will be dragged.")
        dragSource = wx.DropSource(self)
        dragSource.SetData(my_data)
        result = dragSource.DoDragDrop(True)