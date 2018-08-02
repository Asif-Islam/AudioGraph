# Represents a tag-value pair described in inputs/outputs/configs
# of a transformer. 

class Link(object):
        
    def __init__(self, tag=None, value=None):
        self.tag = tag
        self.value = value

    def setValue(self, value):
        link = Link(self.tag, value)
        return link

    def get_tag(self):
        return self.tag

    def get_value(self):
        return self.value