import numpy as np
from transformer import *

# Performs linear interpolation after phase
# vocoding is complete. This is done when the
# analysis hop size differs from the synthesis 
# hopsize. The size of the output samples will
# be the floor of the fft length multipled by
# the ratio of analysis to synthesis hopsize.
#
##########
# Inputs #
##########
# INPUT_SAMPLES: Input samples after phase vocoding.
#
###########
# Outputs #
###########
# OUTPUT_SAMPLES: Output samples after linear interpolation
#
###########
# Configs #
###########
# FFT_LENGTH: Expected length of FFT operation. The shape of the input
#             samples must equal to this length.
# ANALYSIS_HOPSIZE: Numerator to the stretch factor for interpolation. 
# SYNTHESIS_HOPSIZE: Denominator to the stretch factor for interpolation.
#
#
# Example AGDL configuration:
#
# Example configuration:
#
# VocoderLinearInterpolator {
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
#       <ANALYSIS_HOPSIZE> 500
#       <SYNTHESIS_HOPSIZE> 512
#
#   }
# }

class VocoderLinearInterpolator(Transformer):
    def __init__(self):
        super(VocoderLinearInterpolator, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_samples_key = "INPUT_SAMPLES"

        # Output Keys.
        self.output_samples_key = "OUTPUT_SAMPLES"

        # Option Keys.
        self.fft_length_key = "FFT_LENGTH"
        self.analysis_hopsize_key = "ANALYSIS_HOPSIZE"
        self.synthesis_hopsize_key = "SYNTHESIS_HOPSIZE"

        # Local variables.
        self.fft_length = configs[self.fft_length_key]

        # Prepare ready inputs for graph.
        self.ready_inputs[self.input_samples_key] = False

    def compute(self):
        # Retrieve inputs.
        samples = self.inputs[self.input_samples_key]
        n = samples.shape[0]
        assert n == self.fft_length

        # Use linear interpolation to generate the output grain after
        # shifting/hanning.
        lx = int(np.floor(n * self.analysis_hopsize / self.synthesis_hopsize))
        x = np.arange(0,lx) * float(n) / float(lx)
        ix = np.floor(x).astype(int)
        ix1 = ix + 1
        dx = x - ix
        dx1 = 1 - dx

        grain1 = np.append(samples, [0])
        grain2 = np.zeros((lx,),dtype=np.float)
        
        for i in range(0, lx):
            grain2[i] = grain1[ix[i]] * dx1[i] + grain1[ix1[i]] * dx[i]

        self.outputs[self.output_samples_key] = grain2
        