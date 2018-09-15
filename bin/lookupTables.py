import numpy as np

class Lookups:

    _sineSamples = 100000
    _sineValues = []
    _squareValues = []
    _sawToothValues = []

    @staticmethod
    def initializeLookups():
        Lookups._sineValues = np.sin(2 * np.pi * np.arange(Lookups._sineSamples) / Lookups._sineSamples)
        Lookups._squareValues = np.sign(np.sin(2 * np.pi * np.arange(Lookups._sineSamples) / Lookups._sineSamples))
        Lookups._sawToothValues = ((np.arange(Lookups._sineSamples) / Lookups._sineSamples) % 1)\
                                      .astype(np.float32) * 2 - 1


    @staticmethod
    def sineValues():
        '''Returns lookup array of sine values with full 2 pi sine period of 100.000 samples'''
        return Lookups._sineValues

    @staticmethod
    def squareValues():
        return Lookups._squareValues

    @staticmethod
    def sawToothValues():
        return Lookups._sawToothValues

    @property
    def sineSamples(self):
        return self._sineSamples

    @property
    def squareSamples(self):
        return self._sineSamples

    @property
    def sawToothSamples(self):
        return self._sineSamples
