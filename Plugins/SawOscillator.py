import wx

from Plugins.Oscillator.SawtoothSound import SawToothSound
from Plugins.Oscillator.SquareSound import SquareSound
from Plugins.SineOscillator import SineOscillator


class SawOscillator(SineOscillator):
    icon = wx.Bitmap('Plugins\icons\sawtooth.png')
    pass

    def set_osc(self):
        self.oscSound = SawToothSound()

    def window_title(self):
        return "Saw Oscillator"

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(SawOscillator, self.get_serialization_data()[1])

    def get_serialization_data(self):
        return ('SawOscillator', {'isSound': True,
                                   'knob1Value': self.knob1.GetValue(),
                                   'knob2Value': self.knob2.GetValue(),
                                   'knob3Value': self.knob3.GetValue(),
                                   'colourRed': self.colourRed,
                                   'colourGreen': self.colourGreen,
                                   'colourBlue': self.colourBlue,
                                   'colourAlpha': self.colourAlpha,
                                   'pluginName': self.instrumentNameTextCtrl.GetValue()})