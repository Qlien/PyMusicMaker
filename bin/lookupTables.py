import numpy as np

class Lookups:

    _sineSamples = 100000
    _sineValues = []

    @staticmethod
    def initializeLookups():
        Lookups._sineValues = np.sin(2 * np.pi * np.arange(Lookups._sineSamples) / Lookups._sineSamples)

    @staticmethod
    def sineValues():
        '''Returns lookup array of sine values with full 2 pi sine period of 100.000 samples'''
        return Lookups._sineValues

    @property
    def sineSamples(self):
        return self._sineSamples
