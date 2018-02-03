import wx
import random
from plugin import PluginBase, PluginType
import wx.lib.agw.knobctrl as KC
import wx.lib.colourselect as csel


class Oscillator(PluginBase):
    icon = wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
    pluginType = PluginType.SOUNDGENERATOR
    def __init__(self, frameParent):
        super(Oscillator, self).__init__(frameParent, PluginType.SOUNDGENERATOR, wx.Bitmap('Plugins\Oscillator\Graphics\icon.png'))

        self.knob1 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.knob2 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.knob3 = KC.KnobCtrl(self, -1, size=(100, 100))

        self.knob1.SetTags(range(0, 101, 5))
        self.knob1.SetAngularRange(-45, 225)
        self.knob1.SetValue(50)

        self.knob2.SetTags(range(0, 101, 5))
        self.knob2.SetAngularRange(-45, 225)
        self.knob2.SetValue(50)

        self.knob3.SetTags(range(0, 101, 5))
        self.knob3.SetAngularRange(-45, 225)
        self.knob3.SetValue(50)

        self.knobtracker1 = wx.StaticText(self, -1, "Value = " + str(self.knob1.GetValue()))
        self.knobtracker2 = wx.StaticText(self, -1, "Value = " + str(self.knob2.GetValue()))
        self.knobtracker3 = wx.StaticText(self, -1, "Value = " + str(self.knob3.GetValue()))

        leftknobsizer_staticbox = wx.StaticBox(self, -1, "Play With Me!")
        middleknobsizer_staticbox = wx.StaticBox(self, -1, "Change My Properties!")
        tightknobsizer_staticbox = wx.StaticBox(self, -1, "Change My Properties!3")

        menusizer_staticbox = wx.StaticBox(self, -1, "Menu")

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        menusizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        menuStaticSizer = wx.StaticBoxSizer(menusizer_staticbox, wx.HORIZONTAL)
        leftknobsizer = wx.StaticBoxSizer(leftknobsizer_staticbox, wx.VERTICAL)
        middleknobsizer = wx.StaticBoxSizer(middleknobsizer_staticbox, wx.VERTICAL)
        rightknobsizer = wx.StaticBoxSizer(tightknobsizer_staticbox, wx.VERTICAL)

        instrumentNameText = wx.StaticText(self, id=-1, label="Name:")
        instrumentNameTextCtrl = wx.TextCtrl(self, id=-1, value=self.pluginName)

        instrumentColorText = wx.StaticText(self, id=-1, label="Color:")
        instrumentColorPicker = wx.ColourPickerCtrl(self, id=-1,
                                                    colour=wx.Colour(random.randint(0, 255), random.randint(0, 255),
                                                                     random.randint(0, 255), alpha=255))

        saveButton = wx.Button(self, -1, "Save")

        menuStaticSizer.Add(instrumentNameText, 0, wx.ALL|wx.EXPAND, 5)
        menuStaticSizer.Add(instrumentNameTextCtrl, 2, wx.ALL|wx.EXPAND, 5)
        menuStaticSizer.Add(instrumentColorText, 0, wx.ALL|wx.EXPAND, 5)
        menuStaticSizer.Add(instrumentColorPicker, 0, wx.ALL|wx.EXPAND, 5)
        menuStaticSizer.Add(saveButton, 0, wx.ALL|wx.EXPAND, 5)

        menusizer.Add(menuStaticSizer, 1, wx.ALL|wx.EXPAND, 5)
        panelsizer.Add(menusizer, 0, wx.EXPAND|wx.ALL)

        rightknobsizer.Add(self.knob1, 1, wx.ALL|wx.EXPAND, 5)
        rightknobsizer.Add(self.knobtracker1, 0, wx.ALL, 5)
        bottomsizer.Add(rightknobsizer, 1, wx.ALL|wx.EXPAND, 5)
        middleknobsizer.Add(self.knob3, 1, wx.ALL|wx.EXPAND, 5)
        middleknobsizer.Add(self.knobtracker3, 0, wx.ALL, 5)
        bottomsizer.Add(middleknobsizer, 1, wx.ALL|wx.EXPAND, 5)
        leftknobsizer.Add(self.knob2, 1, wx.ALL|wx.EXPAND, 5)
        leftknobsizer.Add(self.knobtracker2, 0, wx.ALL, 5)
        bottomsizer.Add(leftknobsizer, 1, wx.ALL|wx.EXPAND, 5)
        panelsizer.Add(bottomsizer, 1, wx.EXPAND|wx.ALL, 20)

        self.SetSizer(panelsizer)
        panelsizer.Layout()

        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.OnAngleChanged1, self.knob1)
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.OnAngleChanged2, self.knob2)
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.OnAngleChanged3, self.knob3)

    def OnAngleChanged1(self, event):

        value = event.GetValue()
        self.knobtracker1.SetLabel("Value = " + str(value))
        self.knobtracker1.Refresh()

    def OnAngleChanged2(self, event):

        value = event.GetValue()
        self.knobtracker2.SetLabel("Value = " + str(value))
        self.knobtracker2.Refresh()

    def OnAngleChanged3(self, event):

        value = event.GetValue()
        self.knobtracker3.SetLabel("Value = " + str(value))
        self.knobtracker3.Refresh()