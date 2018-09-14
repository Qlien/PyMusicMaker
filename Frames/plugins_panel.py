import importlib
import pkgutil

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

import Plugins
from plugin import PluginType


def generate_plugins_panel(parent):
    win = wx.MDIChildFrame(parent, -1, "Plugins", size=(110, 600), pos=(0, 0),
                           style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)
    s = wx.BoxSizer(wx.VERTICAL)
    panel = PluginsPanel(win)
    s.Add(panel, 1, wx.EXPAND)
    win.SetSizer(s)
    return panel

class CheckListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):

    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, wx.ID_ANY, style=wx.LC_REPORT |
                wx.SUNKEN_BORDER | wx.LC_NO_HEADER)
        ListCtrlAutoWidthMixin.__init__(self)

class PluginsPanel(wx.Panel):
    def __init__(self, parent):
        self.frameParent = None
        self.associationData = {}
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self.instrumentsText = wx.StaticText(self, -1, "Instruments")
        self.filtersText = wx.StaticText(self, -1, "Filters")
        # listView initialization
        self.instruments_list = CheckListCtrl(self)

        self.filters_list = CheckListCtrl(self)
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(self.instrumentsText, 0, wx.EXPAND)
        s.Add(self.instruments_list, 1, wx.EXPAND)
        s.Add(self.filtersText, 0, wx.EXPAND)
        s.Add(self.filters_list, 1, wx.EXPAND)
        self.SetSizer(s)

        self.instruments_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnInstrumentsActivated)
        self.filters_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnFiltersActivated)

        self.plugins = self.searchForPlugins()

        self.generateList(size=(50, 50))

        self.instruments_list.SetAutoLayout(True)
        self.Refresh()

    def set_frame_parent(self, frame_parent):
        self.frameParent = frame_parent

    def Destroy(self):
        try:
            super(wx.Panel, self).Destroy()
            self.parent.Destroy()
        except:
            print('already deleted')

    def set_instruments_panel(self, instruments_panel):
        self.instrumentsPanel = instruments_panel

    def generateList(self, size=(50, 50)):

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = 1
        info.m_format = 0
        info.m_text = "Generators"
        self.instruments_list.InsertColumn(0, info)
        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = 1
        info.m_format = 0
        info.m_text = "Filters"
        self.filters_list.InsertColumn(0, info)

        image_list = wx.ImageList(*size)

        for key, (name, plugin) in enumerate(self.plugins.items()):
            classWrapper = getattr(plugin, name[name.find('.') + 1:].title())
            self.associationData[key] = classWrapper
            image = image_list.Add(
                classWrapper.icon.ConvertToImage().Rescale(*size).ConvertToBitmap())
            if classWrapper.pluginType == PluginType.SOUNDGENERATOR:
                item = self.instruments_list.InsertItem(key,
                                                        (name[name.find('.') + 1:]),
                                                        image)
                self.instruments_list.SetItemData(item, key)
                self.instruments_list.SetItemImage(item, image, wx.TreeItemIcon_Normal)

            if classWrapper.pluginType == PluginType.FILTER:
                item = self.filters_list.InsertItem(key,
                                                        (name[name.find('.') + 1:]),
                                                        image)
                self.filters_list.SetItemData(item, key)
                self.filters_list.SetItemImage(item, image, wx.TreeItemIcon_Normal)

        self.instruments_list.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        self.filters_list.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)
        self.Layout()

    # when double clicked
    def OnInstrumentsActivated(self, event):
        itemb = event.GetIndex()
        item = self.instruments_list.GetItemData(itemb)
        classInstance = self.associationData[item](self.frameParent)
        classInstance.set_instruments_panel_window(self.instrumentsPanel)

    def OnFiltersActivated(self, event):
        itemb = event.GetIndex()
        item = self.filters_list.GetItemData(itemb)
        classInstance = self.associationData[item](self.frameParent)
        classInstance.set_instruments_panel_window(self.instrumentsPanel)


    # for finding plugins in folder
    def searchForPlugins(self):
        return {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in self.iter_namespace(Plugins)
        }

    def iter_namespace(self, ns_pkg):
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")
