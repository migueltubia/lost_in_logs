from colorama import Fore, Style
from pygrok import Grok
from console_progressbar import ProgressBar
from netaddr import *


class Engine(object):
    module_name = ""
    description = ""
    
    IPS=[]

    def __init__(self):
        self.module_name = self.get_name()
        self.description = self.get_description()

    def get_name(self):
        pass
        
    def get_description(self):
        pass

    def run(self, file):
        pass

    def checkData(self, _data):
        if not "src_name" in _data.keys() and "src_ip" in _data.keys():
            _data["src_name"]=_data["src_ip"]
        if not "dst_name" in _data.keys() and "dst_ip" in _data.keys():
            _data["dst_name"]=_data["dst_ip"]
        
        if not "src_ip" in _data.keys():
            _data["src_ip"]=""
        if not "dst_ip" in _data.keys():
            _data["dst_ip"]=""
        
        try:
            if (_data["src_ip"]!="" and IPAddress(_data["src_ip"]).is_loopback()) or (_data["dst_ip"]!="" and IPAddress(_data["dst_ip"]).is_loopback()):
                return None
        except:
            return None
        
        if not ("src_name" in _data.keys() and "dst_name" in _data.keys()):
            return None
        
        return _data

    def _run(self, file):
        result=[]
        result_temp = self.run(file)
        for node in result_temp:
            try:
                if self.checkData(node) is not None:
                    src_ip = node["src_ip"]
                    dst_ip = node["dst_ip"]
                    
                    if src_ip!="" and not(IPAddress(src_ip).is_private()) and src_ip not in self.IPS:
                        self.IPS.append(src_ip)
                        
                    if dst_ip!="" and not(IPAddress(dst_ip).is_private()) and dst_ip not in self.IPS:
                        self.IPS.append(dst_ip)
                    
                    result.append(node)
            except:
               pass
            
        return result

class TextEngine(Engine):
    
    pattern = ""

    def __init__(self):
        super().__init__()
        self.pattern = self.get_pattern()

    def get_pattern(self):
        pass

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