####################################################################################################
# 
# Babel - A Bibliography Manager 
# Copyright (C) Salvaire Fabrice 2013 
# 
####################################################################################################

####################################################################################################

import numpy as np

####################################################################################################

from Babel.Tools.Binning import Binning1D

####################################################################################################

class Histogram(object):

    ##############################################

    def __init__(self, binning):

        # Fixme: direct mode

        if isinstance(binning, Binning1D):
            self._binning = binning
        else:
            raise ValueError

        array_size = self._binning.array_size
        self._accumulator = np.zeros(array_size)
        self._sum_weight_square = np.zeros(array_size)
        self._errors = np.zeros(array_size)
        
        self._errors_are_dirty = True

    ##############################################
        
    @property
    def binning(self):

        return self._binning

    ##############################################
        
    @property
    def accumulator(self):

        return self._accumulator

    ##############################################
        
    def __iadd__(self, obj):

        if self.is_consistent_with(obj):
            self._accumulator += obj._accumulator
        else:
            raise ValueError

    ##############################################
        
    def is_consistent_with(self, obj):

        return self._binning == obj._binning

    ##############################################
        
    def clear(self, value=.0):

        self._accumulator[:] = value
        self._sum_weight_square[:] = value**2
        self._errors_are_dirty = True

    ##############################################
        
    def fill(self, x, weight=1.):

        if weight < 0:
            raise ValueError

        i = self._binning.find_bin(x)
        self._accumulator[i] += weight
        # if weight == 1.: weight_square = 1.
        self._sum_weight_square[i] += weight**2
        self._errors_are_dirty = True

    ##############################################
        
    def compute_errors(self):

        if self._errors_are_dirty:
            self._errors = np.sqrt(self._sum_weight_square)

    ##############################################
        
    def get_bin_error(self, i):

        self.compute_errors()
            
        return self._errors[i]

    ##############################################
        
    def integral(self):

        return self._accumulator.sum()

    ##############################################
        
    def normalise(self):

        self._accumulator /= self.integral()
        self._errors_are_dirty = True

    ##############################################
        
    def to_graph(self):

        self.compute_errors()

        binning = self._binning
        bin_slice = binning.bin_slice()

        x_values = binning.bin_centers()

        y_values = np.copy(self._accumulator[bin_slice])
        y_errors = np.copy(self._errors[bin_slice])

        x_errors = np.empty(x_values.shape)
        x_errors[:] = .5*binning.bin_width

        return x_values, y_values, x_errors, y_errors

   ###############################################
        
    def __str__(self):

        binning = self._binning

        string_format = """
Histogram 1D
  interval: %s
  number of bins: %u
  bin width: %g
"""

        text = string_format % (str(binning._interval), binning._number_of_bins, binning._bin_width)
        for i in binning.bin_iterator(xflow=True):
            text += '%3u %s = %g +- %g\n' % (i,
                                             str(binning.bin_interval(i)),
                                             self._accumulator[i],
                                             self.get_bin_error(i),
                                             )

        return text

####################################################################################################
# 
# End
# 
####################################################################################################