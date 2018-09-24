import numpy as np
from transformer import *

# Performs resynthesis after phase vocoding.
# Undos FFT shifting and windowing done by
# the vocoder analyzer prior to any synthesis 
# operations.
#
##########
# Inputs #
##########
# INPUT_SAMPLES: Input samples after phase vocoding.
#
###########
# Outputs #
###########
# OUTPUT_SAMPLES: Output samples after phase vocoder postprocessing.
#
###########
# Configs #
###########
# FFT_LENGTH: Expected length of FFT operation. The shape of the input
#             samples must equal to this length.
#
# Example AGDL configuration:
#
# Example configuration:
#
# VocoderResynthesizer {
#   inputs
#   {
#       <INPUT_SAMPLES> input_samples
#   }   
#   outputs 
#   {
#       <OUTPUT_SAMPLES> output_samples
#   }
#   configs
#   {
#       <FFT_LENGTH> 2048
#   }
# }

class VocoderResynthesizer(Transformer):
    def __init__(self):
        super(VocoderResynthesizer, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_samples_key = "INPUT_SAMPLES"

        # Output Keys.
        self.output_samples_key = "OUTPUT_SAMPLES"

        # Option Keys.
        self.fft_length_key = "FFT_LENGTH"

        # Local variables.
        self.fft_length = configs[self.fft_length_key]

        # Prepare ready inputs for graph.
        self.ready_inputs[self.input_samples_key] = False

    def compute(self):
        # Retrieve inputs.
        samples = self.inputs[self.input_samples_key]

        # Assume for now that the shape of the input samples is exactly
        # equal to the intended FFT length. 
        n = samples.shape[0]
        assert n == self.fft_length
        assert self.fft_length % 2 == 0

        # FFT shift.
        output = np.concatenate([samples[n/2:], samples[0:n/2]])

        # Apply a Hanning window to the samples as postprocessing.
        # TODO: Move hanning window function to a separate helper class.
        for i in range(0, n):
            window_value = -0.5 * np.cos(2.0 * np.pi * float(i) / float(self.fft_length)) + 0.5
            output[i] = output[i] * window_value

        self.outputs[self.output_samples_key] = output