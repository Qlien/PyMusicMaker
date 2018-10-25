import random
import pyaudio

import numpy as np
import wx
import wx.lib.agw.knobctrl as KC

from Plugins.Oscillator.OscSound import OscSound
from bin.plugin import PluginBase, PluginType



class DrumB(PluginBase):
    icon = wx.Bitmap('Plugins\icons\\drum.png')
    pluginType = PluginType.SOUNDGENERATOR

    def __init__(self, frameParent, **kwargs):
        super(DrumB, self).__init__(frameParent, PluginType.SOUNDGENERATOR
                                      , wx.Bitmap('Plugins\Oscillator\Graphics\icon.png')
                                      , name=kwargs.get('pluginName', 'DrumB'))

        self.instrumentsPanel = None

        self.knob1 = KC.KnobCtrl(self, -1, size=(100, 100))
        self.isSound = kwargs.get('isSound', False)

        self.knob1.SetTags(range(0, 101, 5))
        self.knob1.SetAngularRange(-45, 225)
        self.knob1.SetValue(kwargs.get('knob1Value', 0))

        self.oscSound = OscSound()

        self.oscSound.update_noise_parameter(self.knob1.GetValue())

        self.knobtracker1 = wx.StaticText(self, -1, "Value = " + str(self.knob1.GetValue()))

        self.knob1BeforeSave = self.knob1.GetValue()

        leftknobsizer_staticbox = wx.StaticBox(self, -1, "Drum colour B parameter")

        panelsizer = wx.BoxSizer(wx.VERTICAL)
        menusizer = wx.BoxSizer(wx.HORIZONTAL)
        bottomsizer = wx.BoxSizer(wx.HORIZONTAL)
        leftknobsizer = wx.StaticBoxSizer(leftknobsizer_staticbox, wx.VERTICAL)
        self.base_menu = self.base_top_window_menu_sizer_getter(
            frameParent, PluginType.SOUNDGENERATOR, DrumB.icon, **kwargs)

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
            p = pyaudio.PyAudio()
            # for paFloat32 sample values must be in range [-1.0, 1.0]
            stream = p.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=44100,
                            output=True,
                            frames_per_buffer=44100)

            stream.start_stream()
            stream.write(np.array([x for x in self.generate_sound()]).astype(np.float32))
            stream.stop_stream()
            stream.close()

            # close PyAudio (7)
            p.terminate()

        event.Skip()

    def generate_sound(self, frequency=440, duration=1.0, sample_rate=44000, bits=16, framesInterval=1024, bpm=128):
        return self.sound_generator(frequency=frequency, duration=duration, sample_rate=sample_rate, bits=bits
                                    , framesInterval=1024, bpm=128)

    def sound_generator(self, frequency=440, duration=1.0, sample_rate=44100, bits=16, framesInterval=1024, bpm=128):
        knobVal = int(self.knob1BeforeSave)
        n_samples = int(round(duration * sample_rate))

        wavetable_size = int(sample_rate // (frequency / 2))
        wavetable = (2 * np.random.randint(0, 2, wavetable_size) - 1).astype(np.float32)

        samples = []
        current_sample = 0
        previous_value = 0
        while len(samples) < n_samples:
            random_sign = 1 if random.randint(0, 101) < knobVal else -1
            wavetable[current_sample] = random_sign * 0.5 * (wavetable[current_sample] + previous_value)
            samples.append(wavetable[current_sample])
            previous_value = samples[-1]
            current_sample += 1
            current_sample = current_sample % wavetable.size
            yield wavetable[current_sample]

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
        return ('DrumB', {'isSound': True,
                            'knob1Value': self.knob1.GetValue(),
                            'colourRed': self.colourRed,
                            'colourGreen': self.colourGreen,
                            'colourBlue': self.colourBlue,
                            'colourAlpha': self.colourAlpha,
                            'pluginName': self.instrumentNameTextCtrl.GetValue()})

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(DrumB, self.get_serialization_data()[1])

    def on_angle_changed1(self, event):

        value = event.GetValue()
        self.knobtracker1.SetLabel("Value = " + str(value))
        self.knobtracker1.Refresh()

    def on_color_changed(self, event):

        self.colourRed = event.GetColour().red
        self.colourGreen = event.GetColour().green
        self.colourBlue = event.GetColour().blue
        self.colourAlpha = event.GetColour().alpha
