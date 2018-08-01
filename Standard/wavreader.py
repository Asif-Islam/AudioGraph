import numpy as np
from scipy.io import wavfile
from transformer import *

# This module is responsible for loading and reading
# a *.wav file.
#
###########
# Outputs #
###########
# SAMPLING_RATE: The sampling rate of the audio file.
# DATA: A signal sent from an audio splitter indicating that the input
#       data received is the final set of samples.              
#
###########
# Configs #
###########
# FILENAME: The filename of the audio wav file.
#
# Example AGDL configuration:
#
# WavReader {
#   outputs
#   {
#       <SAMPLING_RATE> sampling_rate
#       <DATA> data
#   }   
#   configs
#   {
#       <FILENAME> "testdata/horn_F.wav"    
#   }
# }

class WavReader(Transformer):
    def __init__(self):
        super(WavReader, self).__init__()

    def initialize(self, configs):
        # Output Keys.
        self.sampling_rate_key = "SAMPLING_RATE";
        self.data_key = "DATA";

        # Option Keys.
        self.file_name_key = "FILENAME";
      
        # Retrieve options
        assert configs[self.file_name_key] != None;
        self.file = configs[self.file_name_key];

    def compute(self):
        # Wavefile.read returns un-normalized data
        # as an numpy array.
        sampling_rate, data = wavfile.read(self.file);
        
        # Construct outputs.
        self.outputs[self.sampling_rate_key] = sampling_rate;
        self.outputs[self.data_key] = data;
