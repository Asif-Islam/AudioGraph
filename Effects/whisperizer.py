import numpy as np
from transformer import *

# Applies a pseudo whisper effect by taking the magnitude
# of the input frequency and spectrum and applying a phase
# shift from a uniformly distrubtion random variable between
# 0 and 1. 
#
##########
# Inputs #
##########
# INPUT_FREQUENCIES: Input frequency spectrum of samples.
#
###########
# Outputs #
###########
# OUTPUT_FREQUENCIES: Output frequency spectrum of samples after whisperization.
#
# Example AGDL configuration:
#
# Whisperizer {
#   inputs
#   {
#       <INPUT_FREQUENCIES> input_frequencies
#   }   
#
#   outputs 
#   {
#       <OUTPUT_FREQUENCIES> output_frequencies
#   }
# }

class Whisperizer(Transformer):
    def __init__(self):
        super(Whisperizer, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_frequencies_key = "INPUT_FREQUENCIES";

        # Output Keys.
        self.output_frequencies_key = "OUTPUT_FREQUENCIES";
                    
        # Prepare ready inputs for graph execution.
        self.ready_inputs[self.input_frequencies_key] = False;

    def compute(self):
        # Retrieve inputs.
        freq = self.inputs[self.input_frequencies_key]
        
        # Take magnitude and add random phase.
        output_freq = [np.abs(f) * np.complex(0, np.random.uniform()) for f in freq]
        
        # Apply to output.
        self.outputs[self.output_frequencies_key] = output_freq