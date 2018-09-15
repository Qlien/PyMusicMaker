import numpy as np

from Plugins.Oscillator.OscSound import OscSound
from bin.lookupTables import Lookups


class SawToothSound(OscSound):
    pass

    def sound_generator(self, frequency=440, duration=1.0, sample_rate=44000, bits=16, framesInterval=1024, bpm=128):
        n_samples = int(round(duration * sample_rate))

        current_interval_index = 0
        while current_interval_index < n_samples:
            simpleSine = Lookups.sawToothValues()[int(((current_interval_index
                                     * (frequency + (frequency * self.dampingParameter / 50)) / sample_rate) % 1)
                                     * len(Lookups.sawToothValues()))]
            simpleSine = self.add_noise(simpleSine)
            simpleSine = self.add_fading(simpleSine, n_samples, current_interval_index)
            yield simpleSine
            current_interval_index += 1
        pass