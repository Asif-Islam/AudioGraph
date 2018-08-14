import numpy as np
from transformer import *

# This module is responsible for performing postprocessing after running IFFT.
# This includes un-normalizing the input vector after IFFT.
#
##########
# Inputs #
##########
# SAMPLES: The samples to apply FFT onto.
#
###########
# Outputs #
###########
# FREQUENCIES: A vector containing a complex representation of the 
#              intensity of each frequency, where each bin i represents
#              the frequency of i * sampling_rate / fft_length
#
###########
# Configs #
###########
# FFT_LENGTH: The intended length of the FFT. Usually should be
#             a power of 2.
#
# Example AGDL configuration:
#
# FFT {
#   inputs:
#   {
#       <SAMPLES> input_data
#   }   
#   outputs: 
#   {
#       <FREQUENCIES> output_data
#   }   
#   configs:
#   {
#       <FFT_LENGTH> 80    
#   }
# }

class FFT(Transformer):
    def __init__(self):
        super(FFT, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_data_key = "SAMPLES";

        # Output Keys.
        self.output_data_key = "FREQUENCIES";

        # Option Keys.
        self.fft_length_key = "FFT_LENGTH";
        self.debug_key = "DEBUG";

        # Retrieve options
        assert configs[self.fft_length_key] != None;
        self.fft_length = configs[self.fft_length_key];
        self.debug = False
        if self.debug_key in configs:
            self.debug = configs[self.debug_key];


        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_data_key] = False;

    def compute(self):
        samples = self.inputs[self.input_data_key]
        samples_shape = np.shape(samples)

        # The length of the sample cannot be longer than the FFT length
        assert samples_shape[0] <= self.fft_length;

        # Pad the sample with zeros if the number of samples is less than the fft length
        if (self.fft_length > samples_shape[0]):
            np.pad(samples, (0, self.fft_length - samples_shape[0]), 'constant', constant_values=(0,0));
        
        # Call recursive fft function and return that to output_data
        self.outputs[self.output_data_key] = self.fft(samples);

    # Implements the Cooley-Tukey Algorithm recursive algorithm for FFT.
    def fft(self, samples):
        N = samples.shape[0]
        if (N == 1):
            return samples;

        even_fft = self.fft(samples[::2]);
        odd_fft = self.fft(samples[1::2]);
        odd_scale_factor = np.exp(-2 * 1j * np.pi * np.arange(N/2) / N);
        
        return np.concatenate([even_fft + odd_scale_factor * odd_fft,
                               even_fft - odd_scale_factor * odd_fft])