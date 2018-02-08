import numpy as np

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

    def generate_sound(self, frequency=440, duration=1.0, sample_rate=44000, bits=16):
        import math
        n_samples = int(round(duration * sample_rate))

        buf = np.zeros(n_samples, dtype=np.int16)
        max_sample = 2 ** (bits - 1) - 1

        sine_multiplier = (float(self.dampingParameter) / 50.0) + 0.1
        last_part_fade_start = sample_rate / 100
        for s in range(n_samples):
            t = float(s) / sample_rate  # time in seconds
            buf[s] = int(round(max_sample * math.sin(2 * math.pi * frequency * t * sine_multiplier) * (
            1 if s < (n_samples - last_part_fade_start) else ((n_samples - s) / last_part_fade_start))))

        buf = self.add_noise(buf)
        buf = self.add_fading(buf)

        return buf

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