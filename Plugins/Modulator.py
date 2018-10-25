import random

import numpy as np
import wx
import wx.lib.agw.knobctrl as KC

from Plugins.Oscillator.OscSound import OscSound
from bin.lookupTables import Lookups
from bin.plugin import PluginBase, PluginType


class Modulator(PluginBase):
    icon = wx.Bitmap('Plugins\icons\\modulator.png')
    pluginType = PluginType.FILTER

    def __init__(self, frameParent, **kwargs):
        super(Modulator, self).__init__(frameParent, PluginType.FILTER
                                      , wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
                                      , name=kwargs.get('pluginName', 'Modulator'))

        self.instrumentsPanel = None

        self.knob1 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.isSound = kwargs.get('isSound', False)

        self.knob1.SetTags(range(0, 101, 5))
        self.knob1.SetAngularRange(-45, 225)
        self.knob1.SetValue(kwargs.get('knob1Value', 41))

        self.knobtracker1 = wx.StaticText(self, -1, "Value = " + str(self.knob1.GetValue()))

        self.knob1BeforeSave = self.knob1.GetValue()

        leftknobsizer_staticbox = wx.StaticBox(self, -1, "Modulator frequency")

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        menusizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        leftknobsizer = wx.StaticBoxSizer(leftknobsizer_staticbox, wx.VERTICAL)
        self.base_menu = self.base_top_window_menu_sizer_getter(
            frameParent, PluginType.FILTER, Modulator.icon, **kwargs)

        self.colourRed = kwargs.get('colourRed', random.randint(0, 255))
        self.colourGreen = kwargs.get('colourGreen', random.randint(0, 255))
        self.colourBlue = kwargs.get('colourBlue', random.randint(0, 255))
        self.colourAlpha = kwargs.get('colourAlpha', 255)

        menusizer.Add(self.base_menu, 1, wx.ALL | wx.EXPAND, 5)
        panelsizer.Add(menusizer, 0, wx.EXPAND | wx.ALL)

        leftknobsizer.Add(self.knob1, 1, wx.ALL | wx.EXPAND, 5)
        leftknobsizer.Add(self.knobtracker1, 0, wx.ALL, 5)
        bottomsizer.Add(leftknobsizer, 1, wx.ALL | wx.EXPAND, 5)
        panelsizer.Add(bottomsizer, 1, wx.EXPAND | wx.ALL, 20)

        self.SetSizer(panelsizer)
        panelsizer.Layout()
        self.sound = None

        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.on_angle_changed1, self.knob1)
        self.Bind(wx.EVT_COLOURPICKER_CHANGED, self.on_color_changed, self.instrumentColorPicker)

    def set_instruments_panel_window(self, instrumentsPanel):
        self.instrumentsPanel = instrumentsPanel

    def on_exit_app(self, event):
        self.show_window(False)

    def on_char(self, event):
        if event.GetUnicodeKey() == wx.WXK_SPACE:
            pass

        event.Skip()

    def get_filter_generator(self, current_sound_wrapper
                             , frequency=440, duration=1.0, sample_rate=44100, bits=16
                             , framesInterval=128, bpm=128):

        knob_value = int(self.knob1BeforeSave)
        n_samples = int(round(duration * sample_rate))

        current_interval_index = 0
        while current_interval_index < n_samples:
            if knob_value > 40:
                yield current_sound_wrapper.currentSoundBuffer[-1]
            simpleSine = np.sin(2 * np.pi * current_interval_index * knob_value / sample_rate)
            yield simpleSine * current_sound_wrapper.currentSoundBuffer[-1]
            current_interval_index += 1
        pass

    def internal_filter_generator(self, previous_sound_array
                                  , current_buffer_array, frequency
                                  , duration, sample_rate, bits):
        pass

    def get_color(self):
        return self.instrumentColorPicker.GetColour()

    def on_close(self, event):
        self.knob1.SetValue(self.knob1BeforeSave)

        print('closing')

    def on_modify(self, event):
        self.knob1BeforeSave = self.knob1.GetValue()

    def get_serialization_data(self):
        return ('Modulator', {'isSound': True,
                            'knob1Value': self.knob1.GetValue(),
                            'colourRed': self.colourRed,
                            'colourGreen': self.colourGreen,
                            'colourBlue': self.colourBlue,
                            'colourAlpha': self.colourAlpha,
                            'pluginName': self.instrumentNameTextCtrl.GetValue()})

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(Modulator, self.get_serialization_data()[1])

    def on_angle_changed1(self, event):

        value = event.GetValue()
        self.knobtracker1.SetLabel("Value = " + str(value))
        self.knobtracker1.Refresh()

    def on_color_changed(self, event):

        self.colourRed = event.GetColour().red
        self.colourGreen = event.GetColour().green
        self.colourBlue = event.GetColour().blue
        self.colourAlpha = event.GetColour().alpha
