import time
from queue import Queue

import numpy as np
import pyaudio

basicNotesKeys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
keys = [3, 4, 5, 6]
firstKeyN = 75


def frequencyFormula(n):
    return (2 ** ((n - 49) / 12)) * 440  # hz


class CurrentSoundWrapper:
    def __init__(self, previousSoundArray, currentSoundBuffer):
        self.currentSoundBuffer = currentSoundBuffer
        self.previousSoundArray = previousSoundArray


class SoundGenerator:
    soundChunksQueue = Queue()
    def __init__(self, sampling_rate=44100):
        self.sampling_rate = sampling_rate
        self.soundPlaying = False
        self.BPM = 128
        self.previousSoundArray = []
        self.sounds = None
        self.filters = None


    def play_song(self, sound_buffer=1024, play_audio=True):
        if self.soundPlaying or not self.sounds:
            return
        self.soundPlaying = True
        last_note_frame = max(self.sounds.keys())
        last_note_frame += max([x.length for x in self.sounds[last_note_frame]])
        current_interval_value = 0
        number_of_frames = int(last_note_frame * self.sampling_rate * 60. / self.BPM)
        current_generators = []
        current_filters_generators = []
        SoundGenerator.soundChunksQueue = Queue()


        if play_audio:
            self.pyAudio = pyaudio.PyAudio()
            # for paFloat32 sample values must be in range [-1.0, 1.0]
            self.stream = self.pyAudio.open(format=pyaudio.paFloat32,
                            channels=1,
                            rate=self.sampling_rate,
                            output=True,
                            frames_per_buffer=self.sampling_rate)

            self.stream.start_stream()

        ct = time.time()
        currentSoundWrapper = CurrentSoundWrapper([], [])

        r = int(self.sampling_rate * 60. / self.BPM)
        while current_interval_value < number_of_frames:
            internal_buffer_counter = 0
            if not self.soundPlaying:
                break

            if current_interval_value % r == 0:
                if len(currentSoundWrapper.currentSoundBuffer) > 0:
                    SoundGenerator.soundChunksQueue.put(np.array(currentSoundWrapper.currentSoundBuffer)
                                                        .astype(np.float32).tobytes())
                    if play_audio:
                        self.stream.write(SoundGenerator.soundChunksQueue.get())
                        currentSoundWrapper.previousSoundArray.extend(currentSoundWrapper.currentSoundBuffer)
                    currentSoundWrapper.currentSoundBuffer = []
                if int(current_interval_value / r) in self.sounds:
                    current_generators.extend([x.plugin.generate_sound(
                        frequency=frequencyFormula(firstKeyN - x.verticalElementPosition)
                        , duration=(60. * x.length / self.BPM), sample_rate=self.sampling_rate
                        , framesInterval=self.sampling_rate, bpm=128) for x in self.sounds[int(current_interval_value / r)]])

                if int(current_interval_value / r) in self.filters:
                    current_filters_generators.extend([x.plugin.get_filter_generator(
                        currentSoundWrapper
                        , frequency=frequencyFormula(firstKeyN - x.verticalElementPosition)
                        , duration=(60. * x.length / self.BPM), sample_rate=self.sampling_rate
                        , framesInterval=self.sampling_rate, bpm=128) for x in self.filters[int(current_interval_value / r)]])

            generators_to_remove = []
            filter_generators_to_remove = []
            generators_counted = 0
            generators_values = 0
            for x in current_generators:
                try:
                    generators_values += next(x)
                    generators_counted += 1
                except StopIteration:
                    generators_to_remove.append(x)
                    generators_counted -= 1

            if generators_counted > 0:
                generators_values /= generators_counted

            for x in generators_to_remove:
                current_generators.remove(x)

            currentSoundWrapper.currentSoundBuffer.append(generators_values)

            for x in current_filters_generators:
                try:
                    currentSoundWrapper.currentSoundBuffer[-1] = next(x)
                except StopIteration:
                    filter_generators_to_remove.append(x)

            for x in filter_generators_to_remove:
                current_filters_generators.remove(x)

            current_interval_value += 1
            internal_buffer_counter += 1

        if play_audio:
            self.stream.stop_stream()
            self.stream.close()
            self.pyAudio.terminate()

        print(time.time() - ct)
        self.soundPlaying = False
        return currentSoundWrapper.previousSoundArray

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
