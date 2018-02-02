import wx
import random
from plugin import PluginBase, PluginType
import wx.lib.agw.knobctrl as KC


class Oscillator(PluginBase, wx.Panel):
    icon = wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
    pluginType = PluginType.SOUNDGENERATOR
    def __init__(self, frameParent):
        super(Oscillator, self).__init__(frameParent, PluginType.SOUNDGENERATOR, wx.Bitmap('Plugins\Oscillator\Graphics\icon.png'))

        win = wx.MDIChildFrame(self.frameParent, -1, "Oscillator", size=(600,400),
                               style=wx.DEFAULT_FRAME_STYLE ^ wx.MINIMIZE_BOX ^ wx.MAXIMIZE_BOX)

        super(wx.Panel, self).__init__(win)
        icn = wx.Icon()
        icn.CopyFromBitmap(self.icon)
        win.SetIcon(icn)
        self.menuElementHeight = 30
        
        menuPanel = wx.Panel(self, -1)
        pluginPanel = wx.Panel(self, -1)
        
        windowSizer = wx.BoxSizer(wx.VERTICAL)
        menuSizer = wx.BoxSizer(wx.HORIZONTAL)
        pluginSizer = wx.BoxSizer(wx.HORIZONTAL)

        instrumentNameText = wx.StaticText(menuPanel, id=-1, label="Instrument Name")
        instrumentNameTextCtrl = wx.TextCtrl(menuPanel, id=-1)

        instrumentColorText = wx.StaticText(menuPanel, id=-1, label="Instrument Color")
        instrumentColorPicker = wx.ColourPickerCtrl(menuPanel, id=-1, colour=wx.Colour(random.randint(0,255), random.randint(0,255), random.randint(0,255), alpha=255))
        
        saveButton = wx.Button(menuPanel, -1, "Save")

        menuSizer.Add(instrumentNameText, -1, wx.ALIGN_LEFT)
        menuSizer.Add(instrumentNameTextCtrl, -1, wx.ALIGN_LEFT)
        menuSizer.Add(instrumentColorText, -1, wx.ALIGN_LEFT)
        menuSizer.Add(instrumentColorPicker, -1, wx.ALIGN_LEFT)
        menuSizer.Add(saveButton, -1, wx.ALIGN_LEFT)
        menuPanel.SetSizer(menuSizer)
        
        knob1 = KC.KnobCtrl(pluginPanel, -1, size=(100, 100))
        pluginSizer.Add(knob1, -1, wx.ALIGN_LEFT)


        
        windowSizer.Add(menuPanel, -1, wx.EXPAND)
        windowSizer.Add(pluginPanel, -1, wx.EXPAND)
        self.SetSizer(windowSizer)
        #hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        #l1 = wx.StaticText(self, -1, "Text Field")

        #hbox1.Add(l1, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        #self.t1 = wx.TextCtrl(self)

        #hbox1.Add(self.t1, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)
        #hbox1.Add(wx.TextCtrl(self), 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)

        #knob1 = KC.KnobCtrl(self, -1, size=(100, 100))
        #knob2 = KC.KnobCtrl(self, -1, size=(100, 100))
        #knob3 = KC.KnobCtrl(self, -1, size=(100, 100))

        #knob1.SetTags(range(0, 151, 10))
        #knob1.SetAngularRange(-45, 225)
        #knob1.SetValue(45)

        #knob2.SetTags(range(0, 151, 10))
        #knob2.SetAngularRange(0, 270)
        #knob2.SetValue(100)
        #knob3.SetTags(range(0, 151, 10))
        #knob3.SetAngularRange(0, 270)
        #knob3.SetValue(100)

        #main_sizer = wx.BoxSizer(wx.VERTICAL)
        #main_sizer.Add(hbox1, 1, wx.EXPAND)
        #main_sizer.Add(knob1, 1, wx.EXPAND)
        #main_sizer.Add(knob2, 1, wx.EXPAND)
        #main_sizer.Add(knob3, 1, wx.EXPAND)

        #self.SetSizer(main_sizer)
        #main_sizer.Layout()

        #s = wx.BoxSizer(wx.VERTICAL)
        #s.Add(self, 1, wx.EXPAND)
        #win.SetSizer(s)