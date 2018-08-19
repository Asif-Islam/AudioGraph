import numpy as np
from transformer import *

# This module is responsible for applying an FIR filter on an input
# audio sample. The following module can replicate a Lowpass, Highpass
# and Bandpass filter.
#
##########
# Inputs #
##########
# SAMPLES: A set of samples to apply filtering on.
# SAMPLING_RATE: The sampling rate of the audio sample.
#
###########
# Outputs #
###########
# FILTERED_SAMPLES: A vector of audio samples after filtering is applied.
#
###########
# Configs #
###########
# FILTER_TYPE: Specifies the the filter type as either LOWPASS, HIGHPASS or BANDPASS.
# FILTER_LENGTH: Specifies the length of the filter.
# LOW_CUTOFF: Specifies the low cutoff frequency for lowpass and bandpass filters.
# HIGH_cUTOFF: Specifies the high cutoff frequency for highpass and bandpass filter.s
#
# Example AGDL configuration:
#
# FIRFilter {
#   inputs
#   {
#       <SAMPLES> samples
#       <SAMPLING_RATE> sampling_rate
#   }   
#   outputs 
#   {
#       <FILTERED_SAMPLES> filtered_samples
#   }   
#   configs
#   {
#       <FILTER_TYPE> LOWPASS
#       <FILTER_LENGTH> 64
#       <LOW_CUTOFF> 500
#       <HIGH_CUTOFF> 300
#   }
# }

class FIRFilter(Transformer):
    def __init__(self):
        super(FIRFilter, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.samples_key = "SAMPLES";
        self.sampling_rate_key = "SAMPLING_RATE";

        # Output Keys.
        self.filtered_samples_key = "FILTERED_SAMPLES";

        # Option Keys.
        self.filter_type_key = "FILTER_TYPE";
        self.filter_length_key = "FILTER_LENGTH";
        self.low_cutoff_key = "LOW_CUTOFF";
        self.high_cutoff_key = "HIGH_CUTOFF";

        assert configs[self.filter_type_key] != None;
        assert configs[self.filter_length_key] != None;
        assert configs[self.filter_length_key] > 0;

        # Local variables.
        self.coefficients = None;
        self.sample_history = [];
        self.filter_type = configs[self.filter_type_key];
        self.filter_length = configs[self.filter_length_key];
        self.low_cutoff = None;
        self.high_cutoff = None;

        if self.filter_type == "LOWPASS":
            assert configs[self.low_cutoff_key] != None;
            self.low_cutoff = configs[self.low_cutoff_key];
        elif self.filter_type == "HIGHPASS":
            assert configs[self.high_cutoff_key] != None;
            self.high_cutoff = configs[self.high_cutoff_key];
        elif self.filter_type == "BANDPASS":
            assert configs[self.low_cutoff_key] != None;
            assert configs[self.high_cutoff_key] != None;
            self.low_cutoff = configs[self.low_cutoff_key];
            self.high_cutoff = configs[self.high_cutoff_key];

        # Prepare ready inputs for graph execution
        self.ready_inputs[self.samples_key] = False;
        self.ready_inputs[self.sampling_rate_key] = False;


    def compute(self):
        # Load inputs.
        samples = self.inputs[self.samples_key]
        sampling_rate = self.inputs[self.sampling_rate_key]

        # Prepare outputs.
        filtered_samples = np.zeros((samples.shape[0],), dtype=np.int16)

        if self.coefficients == None:
            self.compute_coefficients(sampling_rate);

        for i in range(0, samples.shape[0]):
            sample = samples[i]
            result = 0.0;
            self.sample_history.insert(0, sample)
            if len(self.sample_history) > self.filter_length:
                self.sample_history = self.sample_history[:-1]

            # Apply MAC operation with coefficients and samples.
            for j in range(0, len(self.sample_history)):
                result += self.sample_history[j] * self.coefficients[j]
            
            filtered_samples[i] = result;
        
        self.outputs[self.filtered_samples_key] = filtered_samples;

    def compute_coefficients(self, sampling_rate):
        # Initialize our coefficients to an array of 0s.
        self.coefficients = np.zeros((self.filter_length,), dtype=np.float)

        # Compute coefficients based on the type of FIR filter.
        if self.filter_type == "LOWPASS":
            self.compute_lowpass_coefficients(sampling_rate)
        elif self.filter_type == "HIGHPASS":
            self.compute_highpass_coefficients(sampling_rate)
        elif self.filter_type == "BANDPASS":
            self.compute_bandpass_coefficients(sampling_rate)
        
    def compute_lowpass_coefficients(self, sampling_rate):
        alpha = 2 * np.pi * float(self.low_cutoff) / sampling_rate;
        for n in range(0, self.filter_length):
            nn = n - (float(self.filter_length - 1) / 2.0);
            if (nn == 0):
                self.coefficients[n] = alpha / np.pi; 
            else:
                self.coefficients[n] = np.sin(nn * alpha) / (nn * np.pi)

    def compute_highpass_coefficients(self, sampling_rate):
        alpha = 2.0 * np.pi * float(self.high_cutoff) / sampling_rate;
        for n in range(0, self.filter_length):
            nn = n - (float(self.filter_length - 1) / 2.0);
            if (nn == 0):
                self.coefficients[n] = 1.0 - alpha / np.pi; 
            else:
                self.coefficients[n] = -1 * np.sin(nn * alpha) / (nn * np.pi)
        
    def compute_bandpass_coefficients(self, sampling_rate):
        alpha = 2.0 * np.pi * float(self.low_cutoff) / sampling_rate;
        beta = 2.0 * np.pi * float(self.high_cutoff) / sampling_rate;
        for n in range(0, self.filter_length):
            nn = n - (float(self.filter_length - 1) / 2.0);
            if (nn == 0):
                self.coefficients[n] = (beta - alpha) / np.pi; 
            else:
                self.coefficients[n] = (np.sin(nn * beta) - np.sin(nn * alpha)) / (nn * np.pi)
        

    # Override reset ready inputs.
    def resetReadyInputs(self):
        self.ready_inputs[self.samples_key] = False;