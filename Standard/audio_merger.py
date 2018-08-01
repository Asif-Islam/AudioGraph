import numpy as np
from scipy.io import wavfile
from transformer import *

# This module is responsible for concatenating audio samples to a 
# single output vector. The output data of this module is only returned 
# when the final input signal is received.
#
##########
# Inputs #
##########
# INPUT_DATA: A set of samples.
# FINAL_INPUT: A signal sent from an audio splitter indicating that the input
#              data received is the final set of samples.              
#
###########
# Outputs #
###########
# OUTPUT_DATA: A fully concatenated set of samples.
# INPUT_CONSUMED: A signal sent when the merger is merger is ready to accept
#                 the next data sample.
#
# Example AGDL configuration:
#
# AudioMerger {
#   inputs
#   {
#       <INPUT_DATA> input_data
#       <FINAL_INPUT> final_input
#   }   
#   outputs 
#   {
#       <OUTPUT_DATA> output_data
#       <INPUT_CONSUMED> input_consumed
#   }
# }

class AudioMerger(Transformer):
    def __init__(self):
        super(AudioMerger, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_data_key = "INPUT_DATA";
        self.final_input_key = "FINAL_INPUT";

        # Output Keys.
        self.output_data_key = "OUTPUT_DATA";
        self.input_consumed_key = "INPUT_CONSUMED";

        # Local variables for computation.
        self.data = None

        # Pre-emptively set to none so that every time this transformer is triggered.
        self.outputs[self.output_data_key] = None;

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_data_key] = False;
        self.ready_inputs[self.final_input_key] = False;

    def compute(self):
        input_data = self.inputs[self.input_data_key];
        final_input = self.inputs[self.final_input_key];
        
        if self.data is None:
            self.data = np.copy(input_data)
        else:
            self.data = np.concatenate([self.data, input_data])

        self.outputs[self.input_consumed_key] = True;
        if (final_input == True):
            # Send data to output, and nullify input consumed key so that 
            # the audio splitter cannot be triggered any more.
            self.outputs[self.output_data_key] = self.data.astype(np.int16)
            self.outputs[self.input_consumed_key] = None; 
