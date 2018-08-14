import numpy as np
from transformer import *

# This module is responsible for performing IFFT.
#
##########
# Inputs #
##########
# FREQUENCIES: Vector of complex values representing frequency intensities.
#
###########
# Outputs #
###########
# SAMPLES: Reconstructed vector of sample values .
#
###########
# Configs #
###########
# IFFT_LENGTH: The intended length of the IFFT. It is expected that this is the same
#              as the length of the FFT module that converted to the frequency domain
#              initially.
#
# Example AGDL configuration:
#
# IFFT {
#   inputs:
#   {
#       <FREQUENCIES> input_data
#   }   
#   outputs: 
#   {
#       <SAMPLES> output_data
#   }   
#   configs:
#   {
#       <IFFT_LENGTH> 80    
#   }
# }

class IFFT(Transformer):
    def __init__(self):
        super(IFFT, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_data_key = "FREQUENCIES";

        # Output Keys.
        self.output_data_key = "SAMPLES";

        # Option Keys.
        self.ifft_length_key = "IFFT_LENGTH";
        self.debug_key = "DEBUG";

        # Retrieve options
        assert configs[self.ifft_length_key] != None;
        self.ifft_length = configs[self.ifft_length_key];
        self.debug = False
        if self.debug_key in configs:
            self.debug = configs[self.debug_key];

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_data_key] = False;


    def compute(self):
        frequencies = self.inputs[self.input_data_key]
        frequencies_shape = np.shape(frequencies)

        # The length of the frequencies cannot be longer than the FFT length
        assert frequencies_shape[0] <= self.ifft_length;

        # Pad the frequencies with zeros if the number of frequencies is less than the fft length
        if (self.ifft_length > frequencies_shape[0]):
            np.pad(frequencies_shape, (0, self.ifft_length - frequencies_shape[0]), 'constant', constant_values=(0,0));
        
        # Call recursive ifft function and return that to output_data
        self.outputs[self.output_data_key] = np.real(self.ifft(frequencies) / frequencies_shape[0]);


    # Implements the Cooley-Tukey Algorithm recursive algorithm for FFT.
    def ifft(self, frequencies):
        N = frequencies.shape[0]
        if (N == 1):
            return frequencies;

        even_ifft = self.ifft(frequencies[::2]);
        odd_ifft = self.ifft(frequencies[1::2]);
        odd_scale_factor = np.exp(2 * 1j * np.pi * np.arange(N/2) / N);
        
        return np.concatenate([(even_ifft + odd_scale_factor * odd_ifft),
                               (even_ifft - odd_scale_factor * odd_ifft)])