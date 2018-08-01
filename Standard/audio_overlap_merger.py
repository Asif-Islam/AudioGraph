import numpy as np
from scipy.io import wavfile
from transformer import *

# This module is responsible for concatenating audio samples in 
# an overlapping fashion. For portions of the constructed data array
# that is being overlapped, an addition is performed.
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
###########
# Configs #
###########
# OFFSET: Describes how far from the previous position that the next received sample
#         will be overlapped-and-added.
#
# Example AGDL configuration:
#
# AudioOverlapMerger {
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
#   configs  	
#   {
#       <OFFSET> offset
#   }
# }

class AudioOverlapMerger(Transformer):
    def __init__(self):
        super(AudioOverlapMerger, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_data_key = "INPUT_DATA";
        self.final_input_key = "FINAL_INPUT";

        # Output Keys.
        self.output_data_key = "OUTPUT_DATA";
        self.input_consumed_key = "INPUT_CONSUMED";

        # Option Keys.
        self.offset_key = "OFFSET";

        # Local variables for computation.
        self.offset = configs[self.offset_key] 
        self.data = None;

        # Mark the position of the data array that we are currently at.
        # Applies accumulation from the marked position to the end of the array.
        # Pos should increase by offset each iteration.
        self.pos = 0;

        # Pre-emptively set to none so that every time audio_merge is called
        self.outputs[self.output_data_key] = None;

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_data_key] = False;
        self.ready_inputs[self.final_input_key] = False;

    def compute(self):
        input_data = self.inputs[self.input_data_key];
        final_input = self.inputs[self.final_input_key];
        if (self.data == None):
            self.data = np.copy(input_data);
        else:
            # Compute the number of elements from pos to the end of the output, L
            overlap = self.data.shape[0] - self.pos;

            # Apply accumulation from pos->end with [0:L] of the input.
            self.data[self.pos:] += input_data[:overlap];  
            
            # Append [L:] of the input to the output array.
            self.data = np.concatenate([self.data, input_data[overlap:]])

        self.pos += self.offset
        self.outputs[self.input_consumed_key] = True;
        if (final_input == True):
            # Send data to output, and nullify input consumed key so that 
            # the audio splitter cannot be triggered any more.
            self.outputs[self.output_data_key] = self.data.astype(np.int16)
            self.outputs[self.input_consumed_key] = None;
