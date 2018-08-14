import numpy as np
from transformer import *

# This module is responsible for performing preprocessing before 
# running FFT. This includes zero-padding to evenly match the FFT
# length and normalizing FFT values.
#
##########
# Inputs #
##########
# INPUT_SAMPLES: A full set of samples.
#
###########
# Outputs #
###########
# OUTPUT_SAMPLES: The input samples after being processing such as
#                 normailization and padding..
#
# Example AGDL configuration:
#
# FFTPreprocessor {
#   inputs:
#   {
#       <INPUT_SAMPLES> input_samples
#   }   
#   outputs: 
#   {
#       <OUTPUT_SAMPLES> output_samples
#   }   
# }

class FFTPreprocessor(Transformer):
    def __init__(self):
        super(FFTPreprocessor, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_samples_key = "INPUT_SAMPLES";

        # Output Keys.
        self.output_samples_key = "OUTPUT_SAMPLES";

        # Option Keys.
        self.fft_length_key = "FFT_LENGTH";
        self.offset_key = "OFFSET";

        # Retrieve options
        assert configs[self.fft_length_key] != None;
        assert configs[self.offset_key] != None;
        self.fft_length = configs[self.fft_length_key];
        self.offset = configs[self.offset_key];

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_samples_key] = False;

    def compute(self):
        samples = self.inputs[self.input_samples_key]
        max = np.amax(np.abs(samples))
        left_pad = self.fft_length;
        right_pad = self.fft_length - np.mod(samples.shape[0] + left_pad, self.offset)
        output = np.pad(samples, (left_pad, right_pad), 'constant', constant_values=(0,0)).astype(float)
        self.outputs[self.output_samples_key] = output