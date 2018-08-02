# Represents the contents of a transformer described in an audio 
# graph description written in AGDL.

class TFMContent(object):

    def __init__(self, inputs=None, outputs=None, configs=None):
        self.inputs = inputs
        self.outputs = outputs
        self.configs = configs

    def get_inputs(self):
        return self.inputs

    def get_outputs(self):
        return self.outputs

    def get_configs(self):
        return self.configs
    