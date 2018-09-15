import random
from enum import Enum

import wx


class PluginBase(wx.Panel):
    def __init__(self, frameParent, type, icon, name='', **kwargs):
        self.frameParent = frameParent
        self.win = wx.MDIChildFrame(frameParent, -1, name, size=(600, 400),
                                    style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)

        super(wx.Panel, self).__init__(self.win)
        icn = wx.Icon()
        icn.CopyFromBitmap(icon)
        self.win.SetIcon(icn)
        self.pluginName = name
        self.isSound = kwargs.get('isSound', False)

        instrumentNameText = wx.StaticText(self, id=-1, label="Name:")
        self.instrumentNameTextCtrl = wx.TextCtrl(self, id=-1, value=self.pluginName)
        instrumentColorText = wx.StaticText(self, id=-1, label="Color:")

        self.menusizer_staticbox = wx.StaticBox(self, -1, "Menu")
        self.menuStaticSizer = wx.StaticBoxSizer(self.menusizer_staticbox, wx.HORIZONTAL)

        instrumentColorText = wx.StaticText(self, id=-1, label="Color:")
        self.colourRed = kwargs.get('colourRed', random.randint(0, 255))
        self.colourGreen = kwargs.get('colourGreen', random.randint(0, 255))
        self.colourBlue = kwargs.get('colourBlue', random.randint(0, 255))
        self.colourAlpha = kwargs.get('colourAlpha', 255)
        self.instrumentColorPicker = wx.ColourPickerCtrl(self, id=-1,
                                                         colour=wx.Colour(self.colourRed, self.colourGreen,
                                                                          self.colourBlue, alpha=self.colourAlpha))
        if self.isSound:
            self.instrumentNameTextCtrl.Disable()
            self.instrumentColorPicker.Disable()

        saveButton = wx.Button(self, -1, "Modify" if self.isSound else "Generate Sound")

        self.menuStaticSizer.Add(instrumentNameText, 0, wx.ALL | wx.EXPAND, 5)
        self.menuStaticSizer.Add(self.instrumentNameTextCtrl, 2, wx.ALL | wx.EXPAND, 5)
        self.menuStaticSizer.Add(instrumentColorText, 0, wx.ALL | wx.EXPAND, 5)
        self.menuStaticSizer.Add(self.instrumentColorPicker, 0, wx.ALL | wx.EXPAND, 5)
        self.menuStaticSizer.Add(saveButton, 0, wx.ALL | wx.EXPAND, 5)

        self.frameParent = frameParent
        self.icon = icon
        self.pluginType = type
        self.iconSize = (100, 50)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_char)
        self.SetSizer(self.menuStaticSizer)
        self.menuStaticSizer.Layout()
        if self.isSound:
            self.win.Bind(wx.EVT_CLOSE, self.on_exit_app)
            self.Bind(wx.EVT_WINDOW_DESTROY, self.on_close)
            self.Bind(wx.EVT_BUTTON, self.on_modify)
        else:
            self.Bind(wx.EVT_BUTTON, self.on_save)

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(PluginBase, self.get_serialization_data()[1])

    def on_exit_app(self, event):
        self.show_window(False)

    def on_char(self, event):
        if event.GetUnicodeKey() == wx.WXK_SPACE:
            pass
        event.Skip()

    def generate_sound(self, parentWindow):
        raise NotImplementedError

    def show_window(self, show):
        self.win.Show() if show else self.win.Hide()

    def is_window_visible(self):
        return self.win.IsShown()

    def set_instruments_panel_window(self, instrumentsPanel):
        self.instrumentsPanel = instrumentsPanel

    def get_color(self):
        return self.instrumentColorPicker.GetColour()

    def on_close(self, event):
        print('closing')

    def on_modify(self, event):
        pass

class PluginType(Enum):
    SOUNDGENERATOR = 1
    FILTER = 2
    SOUND = 4
