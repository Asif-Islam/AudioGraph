import numpy as np

class GraphRunner(object):

    def __init__(self):
        self.roots = [];
        self.execute_list = [];
        self.num_cycles = 0;

    # Core execution. Runs multiple iterations of BFS until the finish signal is fired.
    def run(self):
        print "Executing Cycle 0";
        for root in self.roots:
            # Call compute function on transformer and retrieve outputs
            root.compute();

            # Pass outputs from parent to child and retrieve a list of all
            # children that are ready to execute in the next cycle 
            ready_children = root.notifyChildren();
            self.execute_list.extend(ready_children);

            # Increment statistics on graph execution
            self.num_cycles = 1;
        
        next_execute_list = []
        while self.execute_list:
            if (self.num_cycles % 100 == 0):
                print "Executing Cycle " + str(self.num_cycles);
            for transformer in self.execute_list:
                transformer_outputs = transformer.compute();
                ready_children = transformer.notifyChildren();
                next_execute_list.extend(ready_children);
            self.num_cycles += 1;
            self.execute_list = next_execute_list[:]
            next_execute_list = []

        print "Completed graph execution after: " + str(self.num_cycles) + " cycles.    "

    def addRoot(self, root):
        self.roots.append(root);
        