import numpy as np
from scipy.io import wavfile
from transformer import *

# This module is responsible for writing a *.wav file.
# 
###########
# Inputs #
###########
# DATA: The vector of samples to be written to the output file.
# SAMPLING_RATE: The sampling rate of the audio file.
#
###########
# Configs #
###########
# FILENAME: The filename of the output audio wav file.
#
# Example AGDL configuration:#
# WavWriter {
#   inputs:
#   {
#       <DATA> data
#       <SAMPLING_RATE> sampling_rate
#   }   
#   outputs: {}   
#   configs:
#   {
#       <FILENAME> "output.wav"    
#   }
# }

class WavWriter(Transformer):
    def __init__(self):
        super(WavWriter, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.data_key = "DATA";
        self.sampling_rate_key = "SAMPLING_RATE";

        # Option Keys.
        self.file_name_key = "FILENAME";

        # Retrieve options
        assert configs[self.file_name_key] != None;
        self.filename = configs[self.file_name_key];

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.data_key] = False;
        self.ready_inputs[self.sampling_rate_key] = False;

    def compute(self): 
        data = self.inputs[self.data_key]; 
        sampling_rate = self.inputs[self.sampling_rate_key];
        wavfile.write(self.filename, sampling_rate, data);
