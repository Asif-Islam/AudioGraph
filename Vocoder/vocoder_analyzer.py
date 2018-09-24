import numpy as np
from transformer import *

# Performs the analysis stage for the vocoder except for FFT.
# Applies a Hanning window and performs an FFT shift. 
# The vocoder analysis should feed into an FFT module.
#
##########
# Inputs #
##########
# INPUT_SAMPLES: Input samples to go through phase vocoding.
#
###########
# Outputs #
###########
# OUTPUT_SAMPLES: Output samples after phase vocoder preprocessing.
#
###########
# Configs #
###########
# FFT_LENGTH: Expected length of FFT operation. The shape of the input
#             samples must equal to this length.
#
# Example AGDL configuration:
#
# VocoderAnalyzer {
#   inputs
#   {
#       <INPUT_SAMPLES> samples
#   }   
#   outputs 
#   {
#       <OUTPUT_SAMPLES> output_samples
#   }   
#   configs
#   {
#       <FFT_LENGTH> fft_length
#   }
# }

class VocoderAnalyzer(Transformer):
    def __init__(self):
        super(VocoderAnalyzer, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_samples_key = "INPUT_SAMPLES"

        # Output Keys.
        self.output_samples_key = "OUTPUT_SAMPLES"

        # Option Keys.
        self.fft_length_key = "FFT_LENGTH"

        # Local variables.
        assert self.fft_length_key in configs
        self.fft_length = configs[self.fft_length_key]

        # Prepare ready inputs for graph execution.
        self.ready_inputs[self.input_samples_key] = False

    def compute(self):
        # Retrieve inputs.
        samples = self.inputs[self.input_samples_key]
        
        # Assume for now that the shape of the input samples is exactly
        # equal to the intended FFT length. 
        n = samples.shape[0]
        assert n == self.fft_length
        assert self.fft_length % 2 == 0

        # Apply a Hanning window to the samples as preprocessing.
        # TODO: Move hanning window function to a separate helper class.
        for i in range(0, n):
            window_value = -0.5 * np.cos(2.0 * np.pi * float(i) / float(n)) + 0.5
            samples[i] = samples[i] * window_value
        
        # Perform an FFT shift.
        output = np.concatenate([samples[n/2:], samples[0:n/2]])
        self.outputs[self.output_samples_key] = output