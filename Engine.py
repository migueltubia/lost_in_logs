from colorama import Fore, Style
from pygrok import Grok
from console_progressbar import ProgressBar
from netaddr import *

class Engine(object):
    module_name = ""
    pattern = ""
    description = ""
    
    IPS=[]

    def __init__(self):
        self.module_name = self.get_name()
        self.description = self.get_description()
        self.pattern = self.get_pattern()

    def get_name(self):
        pass
        
    def get_description(self):
        pass
    
    def get_pattern(self):
        pass

    def run(self, file):
        pass
        
    def _run(self, file):
        result=[]
        result = self.run(file)
        for node in result:
            src_ip = node["src_ip"]
            dst_ip = node["dst_ip"]
            
            if not(IPAddress(src_ip).is_private()) and src_ip not in self.IPS:
                self.IPS.append(src_ip)
                
            if not(IPAddress(dst_ip).is_private()) and dst_ip not in self.IPS:
                self.IPS.append(dst_ip)
            
        return result

class TextEngine(Engine):
    def __init__(self):
        super().__init__()

    def run (self, file):
        _file = open(file, 'r')
        _lines = _file.readlines()
        pb = ProgressBar(total=len(_lines),prefix="Progress", suffix='Now', decimals=3, length=75, fill='X', zfill='-')
        count = 0
        
        grok=Grok(self.pattern)
        
        result=[]
        
        for _line in _lines:
            count +=1
            pb.print_progress_bar(count)
            grok_result = grok.match(_line)
            if grok_result is not None:
                grok_result["source"] = self.get_name()
                result.append(grok_result)
        return result
