# Represents a transformer described in an audio graph description
# written in AGDL.

class Transformer(object):

    def __init__(self, name, tfm_content=None):
        self.name = name
        self.tfm_content = tfm_content

    def set_tfm_content(self, tfm_content):
        transformer = Transformer(self.name, tfm_content)
        return transformer
    
    def get_name(self):
        return self.name

    def get_tfm_content(self):
        return self.tfm_content