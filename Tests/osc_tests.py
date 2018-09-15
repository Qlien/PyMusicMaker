import numpy as np
import unittest

import time
import wx
from Plugins.Oscillator.OscSound import OscSound


class MyDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'Test')
        wx.Button(self, wx.ID_OK)


class TestMyDialog(unittest.TestCase):

    def setUp(self):
        self.osc = OscSound()
        self.osc.dampingParameter = 0
        self.osc.noiseParameter = 0
        self.osc.fadingParameter = 0

    def test_sound_generation_time(self):
        start = time.clock()
        self.osc.generate_sound()
        elapsed = time.clock() - start
        self.assertTrue(elapsed < 0.5)

    def test_sound_generation_time2(self):
        start = time.clock()
        self.osc.generate_sound(duration=10)
        elapsed = time.clock() - start
        self.assertTrue(elapsed < 2)

    def test_sound_fading_time1(self):
        start = time.clock()
        self.osc.add_fading(np.random.randint(-20000, 20000, 44000*10))
        elapsed = time.clock() - start
        self.assertTrue(elapsed < 2)

    def test_sound_noise_time1(self):
        start = time.clock()
        self.osc.add_noise(np.random.randint(-20000, 20000, 44000*10))
        elapsed = time.clock() - start
        self.assertTrue(elapsed < 2)