import wx

from Plugins.Oscillator.SquareSound import SquareSound
from Plugins.SineOscillator import SineOscillator


class SquareOscillator(SineOscillator):
    icon = wx.Bitmap('Plugins\icons\square.png')
    pluginName = "Square Osc"
    pass

    def set_osc(self):
        self.oscSound = SquareSound()

    def window_title(self):
        return "Square Oscillator"

    def on_save(self, event):
        self.instrumentsPanel.add_instrument(SquareOscillator, self.get_serialization_data()[1])

    def get_serialization_data(self):
        return ('SquareOscillator', {'isSound': True,
                                   'knob1Value': self.knob1.GetValue(),
                                   'knob2Value': self.knob2.GetValue(),
                                   'knob3Value': self.knob3.GetValue(),
                                   'colourRed': self.colourRed,
                                   'colourGreen': self.colourGreen,
                                   'colourBlue': self.colourBlue,
                                   'colourAlpha': self.colourAlpha,
                                   'pluginName': self.instrumentNameTextCtrl.GetValue()})