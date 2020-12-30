from Engine import Engine
import Evtx.Evtx as evtx
import xmltodict
import json
from console_progressbar import ProgressBar

class WinEvtx(Engine):

    PATTERNS=[]
    SECURITY_4624={"Provider":"Microsoft-Windows-Security-Auditing","EventID":"4624","data":{},"Pattern":{"src_ip":"IpAddress", "src_port":"IpPort"}}
    RDP_1024={"Provider":"Microsoft-Windows-TerminalServices-ClientActiveXCore","EventID":"1024","data":{},"Pattern":{"src_name":"Value"},"Meta":{"application":"RDP"}}


    def __init__(self):
        super().__init__()
        self.createPatterns()
        
    def get_name(self):
        return "WinEvtx"
        
    def get_description(self):
        return "Parse Windows EVTX files"
        
    def createPatterns(self):
        self.PATTERNS.append(self.SECURITY_4624)
        self.PATTERNS.append(self.RDP_1024)
        
    def getFiles(self, file):
        count = 0
        with evtx.Evtx(file) as log:
            for record in log.records():
                count +=1
        return count
           
    def run (self, file):
        result = []
        count_lines = self.getFiles(file)
        with evtx.Evtx(file) as log:
            pb = ProgressBar(total=count_lines, prefix="Progress", suffix='Now', decimals=3, length=75, fill='X', zfill='-')
            count = 0

            for record in log.records():
                count +=1
                pb.print_progress_bar(count)
                _r=record.xml()
                data_dict = xmltodict.parse(_r)
                json_data = json.dumps(data_dict)
                #print (json_data)
                json_load = json.loads(json_data)
                result_data = self.filterRecord(json_load)
                if result_data != {}:
                    #print (result_data)
                    result.append(result_data)
        return result
        
    def filterRecord(self, record):
        result = {}
        for _pattern in self.PATTERNS:
            filter=True
            if "Provider" in _pattern.keys():
                if not(_pattern["Provider"]==record["Event"]["System"]["Provider"]["@Name"]):
                    filter = False
            if "EventID" in _pattern.keys():
                if not(_pattern["EventID"]==record["Event"]["System"]["EventID"]["#text"]):
                    filter = False
            if "Channel" in _pattern.keys():
                if not(_pattern["Channel"]==record["Event"]["System"]["Channel"]):
                    filter = False
            if "EventData" in _pattern.keys():
                pass
                
            if filter:
                computer_name=record["Event"]["System"]["Computer"]
                result["time"]=record["Event"]["System"]["TimeCreated"]["@SystemTime"]
                if "Pattern" in _pattern.keys():
                    _dp = _pattern["Pattern"]
                    for _keyname, _keyvalue in _dp.items():
                        for _data in record["Event"]["EventData"]["Data"]:
                            _name = _data["@Name"] if "@Name" in _data.keys() else ""
                            _value = _data["#text"] if "#text" in _data.keys() else ""
                            if _name == _keyvalue:
                                result[_keyname]=_value
                    if "Meta" in _pattern.keys():
                        _meta = _pattern["Meta"]
                        for _keyname, _keyvalue in _meta.items():
                            result[_keyname]=_keyvalue
                if not "src_ip" in result.keys() and ("dst_ip" in result.keys() or "dst_name" in result.keys()):
                    result["src_name"] = computer_name
                elif ("src_ip" in result.keys() or "src_name" in result.keys()) and not "dst_ip" in result.keys():
                    result["dst_name"] = computer_name
                
        return result
                