# The following is a recursive descent parser responsible for
# parsing audio processing graph descriptions. The following
# is the first-pass grammar of the audio graph description laguage (AGDL). 
#
# Graph -> (Transformer)+
# Transformer -> Name '{' TFMContent '}'
# TFMContent -> Inputs Outputs Configs
# Inputs -> NULL | 'inputs''{' (Link)+ '}'
# Outputs -> NULL | 'outputs''{' (Link)+ '}'
# Configs -> NULL | 'configs''{' (Link)+ '}'
# IOLink -> '<'Tag'>' Name
# ConfigLink -> '<'Tag'>' [Name | Number | File]
# Name -> [(a-z)|(A-Z)]+
# Tag -> [A-Z]+
# Number -> [1-9][0-9]*
# File -> "(...)"

from lexer import *
from audio_graph import *
from ioc import *
from link import *
from tfm_content import *
from transformer import *


class RDescentGraphParser(object):
    def __init__(self, input_file):
        # Instaintiate a lexer.
        self.lexer = Lexer(input_file)

    # The main parse function which executes on parsing the specified
    # grammar as listed aove. 
    def parse(self):
        return self.audio_graph()

    # Constructs the audio graph as the top level AST structure non-terminal.
    def audio_graph(self):
        audio_graph = AudioGraph(self.transformer())

        while not self.lexer.inspectEOF():
            audio_graph = audio_graph.append(self.transformer())
        
        # Return the constructed AST.
        return audio_graph

    # Constructs a transformer node, consisting of a transformer name
    # and transformer contents.
    def transformer(self):
        transformer = Transformer(self.name())
        self.lexer.consume('{')
        transformer = transformer.set_tfm_content(self.tfm_content())
        self.lexer.consume('}')
        
        return transformer

    # The content of each transform are inputs, outputs and configs.
    # It is possible for inputs/outputs/configs to not be specified
    # in the audio graph description
    def tfm_content(self):
        tfm_content = TFMContent(self.inputs(), self.outputs(), self.configs())
        return tfm_content

    # Inputs, which are defined by a list of links.
    def inputs(self):
        inputs = None
        if self.lexer.inspect('inputs'):
            self.lexer.consume('inputs')
            self.lexer.consume('{')
            inputs = IOC(self.ioLink())
            while not self.lexer.inspect('}'):
                inputs = inputs.append(self.ioLink())
            self.lexer.consume('}')

        return inputs

    # Outputs, which are defined by a list of links.
    def outputs(self):
        outputs = None
        if self.lexer.inspect('outputs'):
            self.lexer.consume('outputs')
            self.lexer.consume('{')
            outputs = IOC(self.ioLink())
            while not self.lexer.inspect('}'):
                outputs = outputs.append(self.ioLink())
            self.lexer.consume('}')

        return outputs

    # Configs, which are defined as a list of links.
    def configs(self):
        configs = None
        if self.lexer.inspect('configs'):
            self.lexer.consume('configs')
            self.lexer.consume('{')
            configs = IOC(self.configLink())
            while not self.lexer.inspect('}'):
                configs = configs.append(self.configLink())
            self.lexer.consume('}')

        return configs

    # An Input/Output Link, which expects link values to only
    # be variable names.
    def ioLink(self):
        self.lexer.consume('<')
        link = Link(self.tag())
        self.lexer.consume('>')
        link = link.setValue(self.name())

        return link

    # A Config Link, which expects link values to either be
    # a variable name, a number or a filepath.
    def configLink(self):
        self.lexer.consume('<')
        link = Link(self.tag())
        self.lexer.consume('>')
        if self.lexer.inspectNumber():
            link = link.setValue(self.number())
        elif self.lexer.inspectName():
            link = link.setValue(self.name())
        else:
            link = link.setValue(self.file())
        return link

    # A tag, which is a fully capitalized name
    def tag(self):
        return self.lexer.consumeTag()

    # Variable name.
    def name(self):
        return self.lexer.consumeName()

    # Numerical values for config links.
    def number(self):
        return self.lexer.consumeNumber()

    # Filepaths for config links.
    def file(self):
        return self.lexer.consumeFile()