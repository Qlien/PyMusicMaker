from Plugins.Oscillator.SawtoothSound import SawToothSound
from Plugins.Oscillator.SquareSound import SquareSound
from Plugins.SineOscillator import SineOscillator


class SawOscillator(SineOscillator):
    pluginName = "Saw Osc"
    pass

    def set_osc(self):
        self.oscSound = SawToothSound()

    def window_title(self):
        return "Square Oscillator"