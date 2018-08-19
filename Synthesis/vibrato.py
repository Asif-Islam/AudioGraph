import numpy as np
from transformer import *

# Applies a vibrato effect using an delay line with an
# FIR Comb Filter.
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
# VIBRATO_SAMPLES: A vector of audio samples after vibrato is applied.
#
###########
# Configs #
###########
# DELAY: Specifies the delay in seconds desired for the vibrato effect.
# MOD_FREQ: Specifies the frequency of a modulation sine wave applied onto
#           in the input samples.
#
# Example AGDL configuration:
#
# Vibrato {
#   inputs:
#   {
#       <SAMPLES> samples
#       <SAMPLING_RATE> sampling_rate
#   }   
#   outputs: 
#   {
#       <VIBRATO_SAMPLES> vibrato
#   }
#   configs:
#   {
#       <DELAY> 0.010
#       <MOD_FREQ> 15
#   }
# }

class Vibrato(Transformer):
    def __init__(self):
        super(Vibrato, self).__init__()

    def initialize(self, configs):
        # Input Keys.
        self.samples_key = "SAMPLES"
        self.sampling_rate_key = "SAMPLING_RATE"

        # Output Keys.
        self.vibrato_samples_key = "VIBRATO_SAMPLES"
    
        # Option Keys.
        self.delay_key = "DELAY"
        self.mod_freq_key = "MOD_FREQ"

        # Local variables.
        assert configs[self.delay_key] != None
        assert configs[self.mod_freq_key] != None
        self.delay = configs[self.delay_key]
        self.mod_freq = configs[self.mod_freq_key]

        # Prepare ready inputs for graph 
        self.ready_inputs[self.samples_key] = False;
        self.ready_inputs[self.sampling_rate_key] = False;

    def compute(self):
        samples = self.inputs[self.samples_key]
        sampling_rate = self.inputs[self.sampling_rate_key]
        
        delay_in_samples = self.delay * sampling_rate
        mod_freq_in_samples = float(self.mod_freq) / sampling_rate

        L = int(2 + delay_in_samples + delay_in_samples*2);
        delay_line = np.zeros((L,), dtype=np.int16)
        vibrato_samples = np.zeros_like(samples)

        for n in range(0, samples.shape[0] - 1):
            mod = np.sin(2 * np.pi * n * mod_freq_in_samples)
            alpha = 1 + delay_in_samples + delay_in_samples * mod;
            i = int(np.floor(alpha))
            factor = alpha - i;
            delay_line = np.concatenate([np.array([samples[n]]), delay_line[0:L-1]])

            # Linear interpolation.
            vibrato_samples[n] = delay_line[i+1] * factor + delay_line[i] * (1 - factor)

            # Spline interpolation.
            # vibrato_samples[n] = delay_line[i+1] * (factor**3) / 6
            # + delay_line[i] * ((1+factor)**3 - 4*(factor**3)) / 6
            # + delay_line[i-1] * ((2-factor)**3 - 4*(1-factor)**3) / 6
            # + delay_line[i-2] * ((1-factor)**3) / 6 

        self.outputs[self.vibrato_samples_key] = vibrato_samples

    # Override reset ready inputs.
    def resetReadyInputs(self):
        self.ready_inputs[self.samples_key] = False;
