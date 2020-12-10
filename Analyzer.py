from colorama import Fore, Style
from console_progressbar import ProgressBar


class Analyzer(object):
    analyzer_name = ""
    description = ""

    def __init__(self):
        self.module_name = self.get_name()
        self.description = self.get_description()

    def get_name(self):
        pass
        
    def get_description(self):
        pass
    
    '''
    Analyze de data and return data.
    This data will be envolved in a structure like:
    {analyzers:[name1:{....},name2:{....}]}
    '''
    def run(self, data):
        pass
        
    def _run(self, data):
        result_analyzer = self.run(data)
        return result_analyzer
