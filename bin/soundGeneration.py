import time

import numpy as np

basicNotesKeys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
keys = [3, 4, 5, 6]
firstKeyN = 28


def frequencyFormula(n):
    return (2 ** ((n - 49) / 12)) * 440  # hz


class SoundGenerator:
    def __init__(self, sampling_rate=44100):
        self.sampling_rate = sampling_rate
        self.soundPlaying = False
        self.BPM = 0.
        self.previousSoundArray = []
        self.sounds = None
        self.filters = None

    def play_song(self, sound_buffer=1024):
        if self.soundPlaying or not self.sounds:
            return
        self.soundPlaying = True
        SoundArray = []
        last_note_frame = max(self.sounds.keys())
        last_note_frame += max([x.length for x in self.sounds[last_note_frame]])
        current_interval_value = 0
        number_of_frames = int(last_note_frame * self.sampling_rate * 60. / self.BPM)
        current_generators = []

        ct = time.time()
        internal_wave_array = []
        r = int(self.sampling_rate * 60. / self.BPM)
        while current_interval_value < number_of_frames:
            internal_buffer_counter = 0
            if current_interval_value % r == 0:
                if len(internal_wave_array) > 0:
                    SoundArray.extend(internal_wave_array)
                    internal_wave_array = []
                if int(current_interval_value / r) in self.sounds:
                    current_generators.extend([x.plugin.generate_sound(
                        frequency=frequencyFormula(x.verticalElementPosition)
                        , duration=(60. * x.length / self.BPM), sample_rate=self.sampling_rate
                        , framesInterval=1024, bpm=128) for x in self.sounds[int(current_interval_value / r)]])

            generators_to_remove = []
            generators_counted = 0
            generators_values = 0
            for x in current_generators:
                try:
                    generators_values = next(x)
                    generators_counted += 1
                except StopIteration:
                    generators_to_remove.append(x)

            if generators_counted > 0:
                generators_values /= generators_counted

            for x in generators_to_remove:
                current_generators.remove(x)

            internal_wave_array.append(generators_values)
            current_interval_value += 1
            internal_buffer_counter += 1

        print(time.time() - ct)
        self.soundPlaying = False
        pass

    def update_sounds(self, soundElements):
        self.sounds = soundElements
        pass

    def update_filters(self, soundElements):
        self.filters = soundElements
        pass

    def set_BPM(self, BPM):
        self.BPM = BPM


class SoundPanelElement:
    def __init__(self, plugin, PluginType, length, verticalElementPosition=0, horizontalElementPosition=0, frequency=0.):
        self.length = length
        self.verticalElementPosition = verticalElementPosition
        self.horizontalElementPosition = horizontalElementPosition
        self.frequency = frequency
        self.PluginType = PluginType
        self.plugin = plugin
