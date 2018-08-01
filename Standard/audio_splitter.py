import numpy as np
from scipy.io import wavfile
from transformer import *

# This module is responsible for splitting the samples of an input
# audio file. 
#
##########
# Inputs #
##########
# INPUT_DATA: A set of samples, e.g. provided from a wav file reader.
# READY: A signal sent from an audio merger indicating that the next split
#        can be performed
#
###########
# Outputs #
###########
# OUTPUT_DATA: A subset of the input audio samples
# FINISHED: A signal sent when no more splitting can be performed
#
###########
# Configs #
###########
# SPLIT_LENGTH: Specifies the length of the output data after splitting
# SPLIT_OFFSET: Specifies the offset that the next split should begin from.
#               Use this for overlapping STFT applications.
#
# Example AGDL configuration:
#
# AudioSplitter {
#   inputs:
#   {
#       <INPUT_DATA> input_data
#       <READY> process_next
#   }   
#   outputs: 
#   {
#       <OUTPUT_DATA> output_data
#       <FINISHED> finished
#   }   
#   configs:
#   {
#       <SPLIT_LENGTH> 80
#       <SPLIT_OFFSET> 40    
#   }
# }

class AudioSplitter(Transformer):
    def __init__(self):
        super(AudioSplitter, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_data_key = "INPUT_DATA";
        self.ready_key = "READY";

        # Output Keys.
        self.output_data_key = "OUTPUT_DATA";
        self.finished_key = "FINISHED";

        # Option Keys.
        self.split_length_key = "SPLIT_LENGTH";
        self.split_offset_key = "SPLIT_OFFSET";
        self.debug_key = "DEBUG";

        # Local variables for computation.
        self.data_position = 0;

        # Retrieve options
        assert configs[self.split_length_key] != None;
        self.split_length = configs[self.split_length_key];
        self.debug = False
        if self.debug_key in configs:
            self.debug = configs[self.debug_key];

        # Split offset is set to the split length unless otherwise specified
        # Specifiying an offset less than the split length means that each
        # adjacent audio segments being returned by this transformer are
        # overlapping by (split_length - split_offset) samples.
        if (configs[self.split_offset_key] != None):
            self.split_offset = configs[self.split_offset_key];
        else:
            self.split_offset = self.split_length;

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_data_key] = False;
        self.ready_inputs[self.ready_key] = True;

    def compute(self):

        data = self.inputs[self.input_data_key];
        num_samples = np.shape(data)[0]

        if (self.data_position + self.split_length > num_samples):
            max_splice_val = num_samples;
        else:
            max_splice_val = self.data_position + self.split_length;

        output_data = data[self.data_position:max_splice_val];
        if self.debug == True:
            print "splicing data from: " + str(self.data_position) + "to" + str(max_splice_val) 
        
        # Increment our position in the sample stream by the offset
        self.data_position += self.split_offset;
        self.outputs[self.finished_key] = self.data_position + self.split_length >= num_samples;

        # Construct outputs.
        self.outputs[self.output_data_key] = output_data;

    # Override reset ready inputs.
    def resetReadyInputs(self):
        self.ready_inputs[self.ready_key] = False;