import numpy as np
from scipy.io import wavfile
from transformer import *

# This module is responsible for loading and reading
# a *.wav file. The path to the wav file must be provided
# as an option.
#
# Example configuration:
#
# WavReader {
#   inputs: {}
#   outputs: 
#   {
#       <SAMPLING_RATE> sampling_rate
#       <DATA> data
#   }   
#   configs:
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
        self.debug_key = "DEBUG";

        # Retrieve options
        assert configs[self.file_name_key] != None;
        self.file = configs[self.file_name_key];
        self.debug = configs[self.debug_key];

    def compute(self):
        # Wavefile.read returns un-normalized data
        # as an numpy array.
        sampling_rate, data = wavfile.read(self.file);
        
        # Handle Debug options.
        if self.debug == True:
            print "WAVREADER: Completed read of " + self.file;
            print "Sampling Rate: " + str(sampling_rate)
            print "Number of samples: " + str(np.shape(data)[0])
            print "Is this audio mono?: " + str(np.shape(data)[1] == 1)

        # Construct outputs.
        self.outputs[self.sampling_rate_key] = sampling_rate;
        self.outputs[self.data_key] = data;
        print np.shape(data)[0]