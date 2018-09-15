from Plugins.Oscillator.SquareSound import SquareSound
from Plugins.SineOscillator import SineOscillator


class SquareOscillator(SineOscillator):
    pluginName = "Square Osc"
    pass

    def set_osc(self):
        self.oscSound = SquareSound()

    def window_title(self):
        return "Square Oscillator"