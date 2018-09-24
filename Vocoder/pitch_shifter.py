import numpy as np
from transformer import *

# Performs the pitch shifting stage of the vocoder.
# The input is expected to to be the output of FFT,
# and the output is modified frequency spectrum. It
# is expected that IFFT follows after this module.
#
##########
# Inputs #
##########
# INPUT_FREQUENCIES: Computed frequencies processed from FFT. 
#
###########
# Outputs #
###########
# OUTPUT_FREQUENCIES: Computed frequencies with pitch shifting applied
#
###########
# Configs #
###########
# FFT_LENGTH : The length of the performed FFT on input samples.
# PITCH_SHIFT_FACTOR: The scaling factor to be applied for phase shifting.
#
# Example AGDL configuration:
#
# PitchShifter {
#   inputs:
#   {
#       <INPUT_FREQUENCIES> input_frequencies
#   }   
#   outputs: 
#   {
#       <OUTPUT_FREQUENCIES> output_frequencies
#   }
#   configs:
#   {
#       <FFT_LENGTH> fft_length
#       <PITCH_SHIFT_FACTOR> pitch_shift_factor
#   }
# }

class PitchShifter(Transformer):
    def __init__(self):
        super(PitchShifter, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.input_frequencies_key = "INPUT_FREQUENCIES";

        # Output Keys.
        self.output_frequencies_key = "OUTPUT_FREQUENCIES";

        # Option Keys.
        self.fft_length_key = "FFT_LENGTH"
        self.pitch_shift_factor_key = "PITCH_SHIFT_FACTOR"

        # Local variables.
        self.fft_length = configs[self.fft_length_key]
        self.pitch_shift_factor = configs[self.pitch_shift_factor_key]
        self.omega = np.zeros((self.fft_length,),dtype=np.float)
        self.prev_phase = np.zeros((self.fft_length,),dtype=np.float)
        self.new_phase = np.zeros((self.fft_length,),dtype=np.float)

        # Holds the "expected" phase offset between two same frequency bins of different fft frames.
        for i in range(0, self.fft_length):
            self.omega[i] = (2 * np.pi * i * self.analysis_hopsize) / self.fft_length;
            
        # Prepare ready inputs for graph execution
        self.ready_inputs[self.input_frequencies_key] = False;

    def compute(self):
        np.set_printoptions(threshold=np.inf)

        # Retrieve inputs.
        freq = self.inputs[self.input_frequencies_key]
        assert freq.shape[0] == self.fft_length

        # Define output.
        output_freq = np.zeros((self.fft_length,), dtype=np.complex)

        magnitude = np.abs(freq)
        phase = np.angle(freq)

        # Compute the new phase based of expected 1) the previous computed phase for this
        # frequency window 2) the difference in phase between this phase and previous phase
        # shifted by scaling factor.
        
        for i in range(0, self.fft_length):
            delta_phase = self.omega[i] + self.phasewrap(phase[i] - self.prev_phase[i] - self.omega[i])
            self.prev_phase[i] = phase[i]
            self.new_phase[i] = self.phasewrap(self.new_phase[i] + delta_phase*self.pitch_shift_factor)
            output_freq[i] = magnitude[i] * np.exp(np.complex(self.new_phase[i]))
        
        self.outputs[self.output_frequencies_key] = output_freq;

    # Wraps the phase between negative PI and positive Pi.
    def phasewrap(self, phase):
        return np.mod(phase + np.pi, -2.0 * np.pi) + np.pi;