# Parse an input AGDL file into an AST and write a python 
# script to execute an audio graph as specified in the file.

from rdescent_graph_parser import *
from audio_graph import *
from ioc import *
from link import *
from tfm_content import *
from transformer import *
from collections import namedtuple

# The following is a map between transformer class name and the filename
# in which they must be imported from. All transformers must be registered
# here for a graph to be correctly generated.

TRANSFORMERS = {}
TRANSFORMERS['AudioSplitter'] = 'audio_splitter'
TRANSFORMERS['AudioMerger'] = 'audio_merger'
TRANSFORMERS['AudioOverlapMerger'] = 'audio_overlap_merger'
TRANSFORMERS['WavReader'] = 'wavreader'
TRANSFORMERS['WavWriter'] = 'wavwriter'

class GraphGenerator(object):

    def __init__(self, agdl_filename, output_filename):
        # Instatiate a parser.
        self.parser = RDescentGraphParser(agdl_filename)
        self.audio_graph_ast = None
        self.lines = []
        self.output_filename = output_filename;
        self.transformer_names = []
        self.input_links = {}
        self.TagWithTFM = namedtuple('TagWithTFM', 'tag tfm_unique_name')

    def generate(self):
        # Preprocessing
        self.audio_graph_ast = self.parser.parse()
        self.initialize_transformer_names()
        self.compute_graph_links()

        # Write python graph script
        self.print_imports()
        self.print_graph_runner()
        self.print_options()
        self.print_transformer_defs()
        self.print_graph_roots()
        self.print_graph_links()
        self.print_footer()

        # Write the output file.
        with open(self.output_filename, 'w') as file:
            for line in self.lines:
                file.write('%s\n' % line)


    def empty_line(self):
        self.lines.append('')

    def initialize_transformer_names(self):
        # Keep a dictionary mapping from transformer to the number of instances
        transformer_to_count = {}

        for tfm in self.audio_graph_ast.get_transformers():
            tfm_name = tfm.get_name()
            tfm_unique_name = ''
            if tfm_name not in TRANSFORMERS:
                raise ValueError('The transformer name ' + name + ' is not registered in the Graph Generator')
            
            if tfm_name in transformer_to_count:
                # Create a unique numbering if there is more than of this type of transformer
                transformer_to_count[tfm_name] = transformer_to_count[tfm_name] + 1
                tfm_unique_name = TRANSFORMERS[tfm_name] + str(transformer_to_count[tfm_name])
            else:
                tfm_unique_name = TRANSFORMERS[tfm_name]
                transformer_to_count[tfm_name] = 1
            
            self.transformer_names.append(tfm_unique_name)

    def print_imports(self):
        self.lines.append("from graph_runner import *")
        
        for tfm in self.audio_graph_ast.get_transformers():
            tfm_name = tfm.get_name()
            tfm_unique_name = ''
            if tfm_name not in TRANSFORMERS:
                raise ValueError('The transformer name ' + name + ' is not registered in the Graph Generator')
            
            self.lines.append("from " + TRANSFORMERS[tfm_name] + " import *")
        
    def print_graph_runner(self):
        self.empty_line()
        self.lines.append('################')
        self.lines.append('# Graph Runner #')
        self.lines.append('################')
        self.lines.append('graph_runner = GraphRunner()')
        self.empty_line()

    def print_options(self):
        # Print the Header.
        self.empty_line()
        self.lines.append('#######################')
        self.lines.append('# Options Definitions #')
        self.lines.append('#######################')
        self.empty_line()

        # Loop over each transformer and define
        # an options dictionary with the specified
        # configs from AGDL file.
        for idx, tfm in enumerate(self.audio_graph_ast.get_transformers()):
            options_name = self.transformer_names[idx] + "_options"

            # Load the options from the transformer
            tfm_content = tfm.get_tfm_content()
            if tfm_content is None:
                raise ValueError('Failed to load the contents of the transformer description')
            configs = tfm_content.get_configs()


            # Printing options dictionary.
            
            # Instantiate dictionary
            self.empty_line()
            self.lines.append(options_name + ' = {}')
            
            # Add each config option
            if configs is not None:
                for link in configs.get_links():
                    tag = link.get_tag()
                    value = link.get_value()
                    self.lines.append(options_name + '["' + tag + '"] = ' + value)

            self.empty_line()

    def print_transformer_defs(self):
        self.empty_line()
        self.lines.append('#############################')
        self.lines.append('# Graph Modules Definitions #')
        self.lines.append('#############################')
        self.empty_line()

        for idx, tfm in enumerate(self.audio_graph_ast.get_transformers()):
            tfm_unique_name = self.transformer_names[idx]
            options_name = tfm_unique_name + '_options'
            self.empty_line()
            self.lines.append(tfm_unique_name + ' = ' + tfm.get_name() + '()')
            self.lines.append(tfm_unique_name + '.initialize(' + options_name + ')')
            self.empty_line()        

    def compute_graph_links(self):
        '''
        Algorithm:
            (1) For each tfm, loop over other input links
            (2) For each link:
            (3)     map the value of the link -> list of all unique_tfm_names that need the input
        
            (4) Once we know the input linkage
                Loop over tfms and for each output link,
                access the list of dependent tfms using the value]
        '''
        
        for idx, tfm in enumerate(self.audio_graph_ast.get_transformers()):
            tfm_unique_name = self.transformer_names[idx]

            # Load the input of the transformer
            tfm_content = tfm.get_tfm_content()
            if tfm_content is None:
                raise ValueError('Failed to load the contents of the transformer description')
            inputs = tfm_content.get_inputs()

            # Loop over each link in the inputs of the TFM
            if inputs is not None:
                for link in inputs.get_links():
                    tag = link.get_tag()
                    value = link.get_value()
                
                    # Each variable (value) maps to a list of tfms that depend on it as input
                    if value in self.input_links:
                        self.input_links[value].append(self.TagWithTFM(tag, tfm_unique_name))
                    else:
                        self.input_links[value] = [self.TagWithTFM(tag, tfm_unique_name)]

    def print_graph_links(self):
        self.empty_line()
        for idx, src_tfm in enumerate(self.audio_graph_ast.get_transformers()):
            src_tfm_unique_name = self.transformer_names[idx]

            # Load the output of the transformer
            src_tfm_content = src_tfm.get_tfm_content()
            if src_tfm_content is None:
                raise ValueError('Failed to load the contents of the transformer description')
            src_outputs = src_tfm_content.get_outputs()

            # Loop over each link in the inputs of the TFM
            if src_outputs is not None:
                for src_link in src_outputs.get_links():
                    src_tag = src_link.get_tag()
                    src_value = src_link.get_value()
                    
                    # Get the list of TFMs depending on this output signal
                    if src_value not in self.input_links:
                        continue
                        
                    sink_tfms = self.input_links[src_value]
                    for sink_tfm in sink_tfms:
                        sink_tag = sink_tfm.tag
                        sink_tfm_unique_name = sink_tfm.tfm_unique_name

                        self.lines.append(src_tfm_unique_name + ".addChild(" + sink_tfm_unique_name + ",{\"" +
                        src_tag + "\":\"" + sink_tag + "\"})")

        self.empty_line()

    def print_footer(self):
        self.empty_line()
        self.lines.append("# Execute the graph.")
        self.lines.append("graph_runner.run()")      

    def print_graph_roots(self):
        self.empty_line()
        self.lines.append('##########################')
        self.lines.append('# Graph Link Definitions #')
        self.lines.append('##########################')
        self.empty_line()

        for idx, tfm in enumerate(self.audio_graph_ast.get_transformers()):
            tfm_unique_name = self.transformer_names[idx]

            # Load the input of the transformer
            tfm_content = tfm.get_tfm_content()
            if tfm_content is None:
                raise ValueError('Failed to load the contents of the transformer description')
            inputs = tfm_content.get_inputs()

            # If there are no inputs, it must be a graph root.
            if inputs is None:
                self.lines.append("graph_runner.addRoot(" + tfm_unique_name + ")")

        self.empty_line()            