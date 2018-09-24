# Represents the top-level AST of an audio graph description
# written in AGDL.

class AudioGraph(object):

    def __init__(self, transformer=None, transformers=None):
        self.transformers = []

        # Inherit all transformers being passed in.
        if transformers is not None:
            self.transformers = transformers

        # Inherit a specific transformer being passed in.
        if transformer is not None:
            self.transformers.append(transformer)
    
    def append(self, transformer):
        audio_graph = AudioGraph(transformer, self.transformers)
        return audio_graph

    def get_transformers(self):
        return self.transformers
        
        

    
