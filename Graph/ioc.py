# Represents inputs/outputs/configs described in the contents of a transformer.

class IOC(object):
        
    def __init__(self, link=None, links=None):
        self.links = []

        # Inherit all transformers being passed in.
        if links is not None:
            self.links = links

        # Inherit a specific transformer being passed in.
        if link is not None:
            self.links.append(link)
            
    def append(self, link):
        ioc = IOC(link, self.links)
        return ioc

    def get_links(self):
        return self.links