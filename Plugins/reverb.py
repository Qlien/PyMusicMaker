import random

import numpy as np
import pygame
import wx
import wx.lib.agw.knobctrl as KC

from Plugins.Oscillator.oscSound import OscillatorSound
from plugin import PluginBase, PluginType


class Reverb(PluginBase):
    icon = wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
    pluginType = PluginType.FILTER

    def __init__(self, frameParent, **kwargs):
        super(Reverb, self).__init__(frameParent, PluginType.FILTER
                                         , wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
                                         , name=kwargs.get('pluginName', 'Reverb'))

        self.instrumentsPanel = None

        self.knob1 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.knob2 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.knob3 = KC.KnobCtrl(self, -1, size=(100, 100))

        self.isSound = kwargs.get('isSound', False)

        self.knob1.SetTags(range(0, 101, 5))
        self.knob1.SetAngularRange(-45, 225)
        self.knob1.SetValue(kwargs.get('knob1Value', 0))

        self.knob2.SetTags(range(0, 101, 5))
        self.knob2.SetAngularRange(-45, 225)
        self.knob2.SetValue(kwargs.get('knob2Value', 0))

        self.knob3.SetTags(range(0, 101, 5))
        self.knob3.SetAngularRange(-45, 225)
        self.knob3.SetValue(kwargs.get('knob3Value', 50))

        self.oscSound = OscillatorSound()

        self.oscSound.update_noise_parameter(self.knob1.GetValue())
        self.oscSound.update_fading_parameter(self.knob2.GetValue())
        self.oscSound.update_damping_parameter(self.knob3.GetValue())

        self.knobtracker1 = wx.StaticText(self, -1, "Value = " + str(self.knob1.GetValue()))
        self.knobtracker2 = wx.StaticText(self, -1, "Value = " + str(self.knob2.GetValue()))
        self.knobtracker3 = wx.StaticText(self, -1, "Value = " + str(self.knob3.GetValue()))

        self.knob1BeforeSave = self.knob1.GetValue()
        self.knob2BeforeSave = self.knob2.GetValue()
        self.knob3BeforeSave = self.knob3.GetValue()

        leftknobsizer_staticbox = wx.StaticBox(self, -1, "Noise")
        middleknobsizer_staticbox = wx.StaticBox(self, -1, "Fading")
        tightknobsizer_staticbox = wx.StaticBox(self, -1, "Damping")

        menusizer_staticbox = wx.StaticBox(self, -1, "Menu")

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        menusizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        menuStaticSizer = wx.StaticBoxSizer(menusizer_staticbox, wx.HORIZONTAL)
        leftknobsizer = wx.StaticBoxSizer(leftknobsizer_staticbox, wx.VERTICAL)
        middleknobsizer = wx.StaticBoxSizer(middleknobsizer_staticbox, wx.VERTICAL)
        rightknobsizer = wx.StaticBoxSizer(tightknobsizer_staticbox, wx.VERTICAL)

        instrumentNameText = wx.StaticText(self, id=-1, label="Name:")
        self.instrumentNameTextCtrl = wx.TextCtrl(self, id=-1, value=self.pluginName)

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

        menuStaticSizer.Add(instrumentNameText, 0, wx.ALL | wx.EXPAND, 5)
        menuStaticSizer.Add(self.instrumentNameTextCtrl, 2, wx.ALL | wx.EXPAND, 5)
        menuStaticSizer.Add(instrumentColorText, 0, wx.ALL | wx.EXPAND, 5)
        menuStaticSizer.Add(self.instrumentColorPicker, 0, wx.ALL | wx.EXPAND, 5)
        menuStaticSizer.Add(saveButton, 0, wx.ALL | wx.EXPAND, 5)

        menusizer.Add(menuStaticSizer, 1, wx.ALL | wx.EXPAND, 5)
        panelsizer.Add(menusizer, 0, wx.EXPAND | wx.ALL)

        leftknobsizer.Add(self.knob1, 1, wx.ALL | wx.EXPAND, 5)
        leftknobsizer.Add(self.knobtracker1, 0, wx.ALL, 5)
        bottomsizer.Add(leftknobsizer, 1, wx.ALL | wx.EXPAND, 5)
        middleknobsizer.Add(self.knob2, 1, wx.ALL | wx.EXPAND, 5)
        middleknobsizer.Add(self.knobtracker2, 0, wx.ALL, 5)
        bottomsizer.Add(middleknobsizer, 1, wx.ALL | wx.EXPAND, 5)
        rightknobsizer.Add(self.knob3, 1, wx.ALL | wx.EXPAND, 5)
        rightknobsizer.Add(self.knobtracker3, 0, wx.ALL, 5)
        bottomsizer.Add(rightknobsizer, 1, wx.ALL | wx.EXPAND, 5)
        panelsizer.Add(bottomsizer, 1, wx.EXPAND | wx.ALL, 20)

        self.SetSizer(panelsizer)
        panelsizer.Layout()
        self.sound = None
        pygame.mixer.pre_init(44000, -16, 1, 512)
        pygame.mixer.init()

        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.on_angle_changed1, self.knob1)
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.on_angle_changed2, self.knob2)
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.on_angle_changed3, self.knob3)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_color_changed, self.instrumentColorPicker)

        if self.isSound:
            self.win.Bind(wx.EVT_CLOSE, self.on_exit_app)
            self.Bind(wx.EVT_WINDOW_DESTROY, self.on_close)
            self.Bind(wx.EVT_BUTTON, self.on_modify)
        else:
            self.Bind(wx.EVT_BUTTON, self.on_save)

    def set_instruments_panel_window(self, instrumentsPanel):
        self.instrumentsPanel = instrumentsPanel

    def on_exit_app(self, event):
        self.show_window(False)

    def on_char(self, event):
        if event.GetUnicodeKey() == wx.WXK_SPACE:
            pygame.mixer.quit()
            pygame.mixer.pre_init(44100, -16, 1, 512)
            pygame.mixer.init(44100, -16, 1, 512)

            sound = pygame.sndarray.make_sound(np.array(self.generate_sound(), dtype=np.int16))
            # play once, then loop forever
            sound.play()

        event.Skip()

    def generate_sound(self, frequency=440, duration=1.0, sample_rate=44000, bits=16):
        self.oscSound.update_damping_parameter(self.knob3.GetValue())
        self.oscSound.update_fading_parameter(self.knob2.GetValue())
        self.oscSound.update_noise_parameter(self.knob1.GetValue())
        return self.oscSound.generate_sound(frequency=frequency, duration=duration, sample_rate=sample_rate, bits=bits)

    def get_color(self):
        return self.instrumentColorPicker.GetColour()

    def on_close(self, event):
        self.knob1.SetValue(self.knob1BeforeSave)
        self.knob2.SetValue(self.knob2BeforeSave)
        self.knob3.SetValue(self.knob3BeforeSave)

        print('closing')

    def on_modify(self, event):
        self.knob1BeforeSave = self.knob1.GetValue()
        self.knob2BeforeSave = self.knob2.GetValue()
        self.knob3BeforeSave = self.knob3.GetValue()

    def get_serialization_data(self):
        return ('Oscillator', {'isSound': True,
                               'knob1Value': self.knob1.GetValue(),
                               'knob2Value': self.knob2.GetValue(),
                               'knob3Value': self.knob3.GetValue(),
                               'colourRed': self.colourRed,
                               'colourGreen': self.colourGreen,
                               'colourBlue': self.colourBlue,
                               'colourAlpha': self.colourAlpha,
                               'pluginName': self.instrumentNameTextCtrl.GetValue()})

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(Reverb, self.get_serialization_data()[1])

    def on_angle_changed1(self, event):

        value = event.GetValue()
        self.knobtracker1.SetLabel("Value = " + str(value))
        self.knobtracker1.Refresh()

    def on_angle_changed2(self, event):

        value = event.GetValue()
        self.knobtracker2.SetLabel("Value = " + str(value))
        self.knobtracker2.Refresh()

    def on_angle_changed3(self, event):

        value = event.GetValue()
        self.knobtracker3.SetLabel("Value = " + str(value))
        self.knobtracker3.Refresh()

    def on_color_changed(self, event):

        self.colourRed = event.GetColour().red
        self.colourGreen = event.GetColour().green
        self.colourBlue = event.GetColour().blue
        self.colourAlpha = event.GetColour().alpha