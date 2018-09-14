import numpy as np

from bin.lookupTables import Lookups


class OscillatorSound:
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
            simpleSine = Lookups.sineValues()[int(((current_interval_index * frequency / sample_rate) % 1)
                                                 * len(Lookups.sineValues()))]
            yield simpleSine
            current_interval_index += 1
        pass

    def add_fading(self, arr):
        arrLen = float(len(arr))
        a = (float(self.fadingParameter) / 10)
        firstPart = (1 / (arrLen ** (2 * a)))
        aTimes2 = a*2
        return [x * (firstPart * (arrLen - k) ** aTimes2) for k, x in enumerate(arr)]

    def add_noise(self, arr):
        if not self.noiseParameter:
            return arr

        noiseValue = float(self.noiseParameter)/100.0
        arrMin = min(arr) * noiseValue
        arrMax = max(arr) * noiseValue

        for k, x in enumerate(arr):
            newValue = x + np.random.randint(low=int(arrMin), high=int(arrMax))
            if newValue < arrMin:
                arr[k] = arrMin
            elif newValue > arrMax:
                arr[k] = arrMax
            else:
                arr[k] = newValue
        return arr