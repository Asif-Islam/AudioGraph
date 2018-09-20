import numpy as np
from transformer import *

# Takes input frequencies and outputs the absolute
# values of the frequencies. Use to apply a robotization
# in a phase vocoding pipeline.
#
##########
# Inputs #
##########
# FREQUENCIES: A vector of complex frequency intensities to operate on.
#
###########
# Outputs #
###########
# ABSOLUTE_FREQUENCIES: A vector of frequency magnitudes.
#
# Example AGDL configuration:
#
# FrequencyAbsoluter {
#   inputs:
#   {
#       <FREQUENCIES> frequencies
#   }   
#   outputs: 
#   {
#       <ABSOLUTE_FREQUENCIES> absolute_frequencies
#   }
# }

class FrequencyAbsoluter(Transformer):
    def __init__(self):
        super(FrequencyAbsoluter, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.frequencies_key = "FREQUENCIES";

        # Output Keys.
        self.absolute_frequencies_key = "ABSOLUTE_FREQUENCIES";
                    
        # Prepare ready inputs for graph execution
        self.ready_inputs[self.frequencies_key] = False;

    def compute(self):
        # Retrieve inputs.
        freq = self.inputs[self.frequencies_key]
        self.outputs[self.absolute_frequencies_key] = np.abs(freq)