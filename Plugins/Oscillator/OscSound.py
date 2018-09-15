import numpy as np

from bin.lookupTables import Lookups


class OscSound:
    def __init__(self):
        self.noiseParameter = 0
        self.dampingParameter = 0
        self.fadingParameter = 0

    def update_noise_parameter(self, noise):
        self.noiseParameter = noise

    def update_fading_parameter(self, noise):
        self.fadingParameter = noise

    def update_damping_parameter(self, noise):
        self.dampingParameter = noise

    def sound_generator(self, frequency=440, duration=1.0, sample_rate=44000, bits=16, framesInterval=1024, bpm=128):
        n_samples = int(round(duration * sample_rate))

        current_interval_index = 0
        while current_interval_index < n_samples:
            simpleSine = Lookups.sineValues()[int(((current_interval_index
                                     * (frequency + (frequency * self.dampingParameter / 50)) / sample_rate) % 1)
                                     * len(Lookups.sineValues()))]
            simpleSine = self.add_noise(simpleSine)
            simpleSine = self.add_fading(simpleSine, n_samples, current_interval_index)
            yield simpleSine
            current_interval_index += 1
        pass

    def add_fading(self, value, soundLen, sample_in_array_no):
        a = (float(self.fadingParameter) / 10)
        firstPart = (1 / (soundLen ** (2 * a)))
        return value * (firstPart * (soundLen - sample_in_array_no) ** (a*2))

    def add_noise(self, value):

        noiseValue = float(self.noiseParameter)/100.0

        newValue = value + np.random.uniform(-1., 1.) * noiseValue
        if newValue < -1:
            value = -1
        elif newValue > 1:
            value = 1
        else:
            value = newValue

        return value
