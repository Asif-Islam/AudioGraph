import numpy as np
from transformer import *

# This module is responsible for performing postprocessing after running IFFT.
# This includes un-normalizing the input vector after IFFT.
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
#                 normailization.
#
# Example AGDL configuration:
#
# FFTPostprocessor {
#   inputs:
#   {
#       <INPUT_SAMPLES> input_samples
#   }   
#   outputs: 
#   {
#       <OUTPUT_SAMPLES> output_samples
#   }   
# }

class FFTPostprocessor(Transformer):
    def __init__(self):
        super(FFTPostprocessor, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_samples_key = "INPUT_SAMPLES";

        # Output Keys.
        self.output_samples_key = "OUTPUT_SAMPLES";

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_samples_key] = False;

    def compute(self):
        samples = self.inputs[self.input_samples_key]
        max = np.amax(np.abs(samples))
        output = np.copy(samples)
        output /= max;
        self.outputs[self.output_samples_key] = output.astype(int16);
        