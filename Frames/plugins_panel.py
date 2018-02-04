import wx
import Plugins
import importlib
import pkgutil
from plugin import PluginType


def generate_plugins_panel(parent, instrumentsPanel):
    win = wx.MDIChildFrame(parent, -1, "Plugins", size=(110,600), pos=(0,0), style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    panel = PluginsPanel(win, parent, instrumentsPanel)
    s.Add(panel, 1, wx.EXPAND)
    win.SetSizer(s)
    win.SetSizeHints(110,600, 1200, 1200)
    win.Show(True)
    return panel

class PluginsPanel(wx.Panel):
    def __init__(self, parent, frameParent, instrumentsPanel):
        self.frameParent = frameParent
        self.associationData = {}
        self.instrumentsPanel = instrumentsPanel
        wx.Panel.__init__(self, parent)

        self.instrumentsText = wx.StaticText(self, -1, "Instruments")
        #listView initialization
        self.listView = wx.ListView(self, -1, style=wx.TR_DEFAULT_STYLE + wx.TR_HIDE_ROOT + wx.TR_HAS_VARIABLE_ROW_HEIGHT)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.instrumentsText, 0, wx.EXPAND)
        s.Add(self.listView, 1, wx.EXPAND)
        self.SetSizer(s)

        self.listView.Bind(wx.EVT_LIST_BEGIN_DRAG, self.OnDragInit)
        self.listView.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivated)

        self.plugins = self.searchForPlugins()

        self.generateList(size=(50,50))

        self.listView.SetAutoLayout(True)

    def generateList(self, size=(50,50)):

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = "Generators"
        self.listView.InsertColumn(0, info)

        image_list = wx.ImageList(*size)

        for key, (name, plugin) in enumerate(self.plugins.items()):
            classWrapper = getattr(plugin, name[name.find('.') + 1:])
            self.associationData[key] = classWrapper
            image = image_list.Add(
                classWrapper.icon.ConvertToImage().Rescale(*size).ConvertToBitmap())
            if classWrapper.pluginType == PluginType.SOUNDGENERATOR:
                item = self.listView.InsertItem(key,
                                                  (name[name.find('.') + 1:]),
                                                  image)
                self.listView.SetItemData(item, key)
                self.listView.SetItemImage(item, image, wx.TreeItemIcon_Normal)

            if classWrapper.pluginType == PluginType.FILTER:
                pass

        self.listView.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        self.Layout()

    #when item starts to be dragged
    def OnDragInit(self, event):
        item = self.listView.GetItemData(event.GetItem())
        text = item.GetText()
        tdo = wx.TextDataObject(text)
        tds = wx.DropSource(self.listView)
        tds.SetData(tdo)
        tds.DoDragDrop(True)


    #when double clicked
    def OnActivated(self, event):
        itemb = event.GetIndex()
        item = self.listView.GetItemData(itemb)
        classInstance = self.associationData[item](self.frameParent)
        classInstance.set_instruments_panel_window(self.instrumentsPanel)

    #for finding plugins in folder
    def searchForPlugins(self):
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in self.iter_namespace(Plugins)
        }

    def iter_namespace(self, ns_pkg):
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")