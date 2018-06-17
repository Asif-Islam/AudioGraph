import numpy as np
from collections import namedtuple

# The base class for all modules used in the computational graph. 

class Transformer(object):

# Every transformer receives input from it's predecessors in
# the graph, and sends an output. Modules can also have config settings
# that are provided at the high level graph description.
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        self.config = {}
        self.children = []
        self.child_tag_connections = []
        self.ready_inputs = {}

        self.ChildTagConnection = namedtuple('ChildTagConnection', 'child tag_map');

    def Initialize(self, configs):
        return True;

    def Compute(self):
        return True;

    def Close(self):
        return True;

    def setInput(self, key, value):
        self.inputs[key] = value;
        self.ready_inputs[key] = True;

    def getOutput(self, key):
        return self.outputs[key]

    def addChild(self, child, tag_map):
        self.children.append(child);
        self.child_tag_connections.append(self.ChildTagConnection(child, tag_map))
    
    def notifyChildren(self):
        ready_children = [];
        for child_tag_connection in self.child_tag_connections:
            child = child_tag_connection.child;
            tag_map = child_tag_connection.tag_map;
            for parent_key, child_key in tag_map.iteritems():
                if (self.outputs[parent_key] != None):
                    child.setInput(child_key, self.outputs[parent_key]);
            if child.readyToExecute():
                ready_children.append(child);
                child.resetReadyInputs();
        
        return ready_children;

    def readyToExecute(self):
        for key, ready_value in self.ready_inputs.iteritems():
            if ready_value == False:
                return False;
        
        return True;

    def resetReadyInputs(self):
        for key, value in self.ready_inputs.iteritems():
            self.ready_inputs[key] = False;
