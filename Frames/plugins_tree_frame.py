import wx
import Plugins
import importlib
import pkgutil
from plugin import PluginType


def generate_plugins_frame(parent):
    win = wx.MDIChildFrame(parent, -1, "Plugins", size=(110,600), pos=(0,0), style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    s.Add(MineDrop(win, parent), 1, wx.EXPAND)
    win.SetSizer(s)
    win.SetSizeHints(110,600, 1200, 1200)
    win.Show(True)

class MineDrop(wx.Panel):
    def __init__(self, parent, frameParent):
        self.frameParent = frameParent
        self.associationData = {}

        wx.Panel.__init__(self, parent)

        self.listctl = wx.ListView(self, -1, style=wx.TR_DEFAULT_STYLE + wx.TR_HIDE_ROOT + wx.TR_HAS_VARIABLE_ROW_HEIGHT)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.listctl, 1, wx.EXPAND)
        self.SetSizer(s)

        plugins = self.searchForPlugins()
        # Add the tree root

        image_list = wx.ImageList(50, 50)

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Generators"
        self.listctl.InsertColumn(0, info)

        for key, (name, plugin) in enumerate(plugins.items()):
            classWrapper = getattr(plugin, name[name.find('.') + 1:])
            classInstance = classWrapper()
            image = image_list.Add(
                classInstance.icon.ConvertToImage().Rescale(50, 50).ConvertToBitmap())
            if classInstance.pluginType == PluginType.SOUNDGENERATOR:
                item = self.listctl.InsertItem(key,
                                                  (name[name.find('.') + 1:]),
                                                  image)
                self.listctl.SetItemData(item, key)
                self.associationData[key] = classInstance
                self.listctl.SetItemImage(item, image, wx.TreeItemIcon_Normal)

            if classInstance.pluginType == PluginType.FILTER:
                pass

        self.listctl.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        #OscillatorImg = image_list.Add(wx.Image("images/grooveshark (Custom).png", wx.BITMAP_TYPE_PNG).Scale(100, 50).ConvertToBitmap())
        self.Centre()
        self.listctl.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnDragInit)
        self.listctl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)

        self.listctl.SetAutoLayout(True)

    #when item starts to be dragged
    def OnDragInit(self, event):
        item = event.GetItem()
        text = item.GetText()
        tdo = wx.TextDataObject(text)
        tds = wx.DropSource(self.listctl)
        tds.SetData(tdo)
        tds.DoDragDrop(True)


    #when double clicked
    def OnActivated(self, event):
        win = wx.MDIChildFrame(self.frameParent, -1, "Plugins",
                               style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)

    #for finding plugins in folder
    def searchForPlugins(self):
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in self.iter_namespace(Plugins)
        }

    def iter_namespace(self, ns_pkg):
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")