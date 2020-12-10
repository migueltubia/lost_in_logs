from Analyzer import Analyzer
from virus_total_apis import PublicApi as VirusTotalPublicApi
import Configuration

class VirusTotal(Analyzer):

    GLOBAL_IPS = {}

    def __init__(self):
        super().__init__()

    def get_name(self):
        return "VirusTotal"
        
    def get_description(self):
        return "Analyze external IPs with Virustotal"
    
    def run(self, data):
        key = Configuration.get_key("VirusTotal", "key")
        if key is None:
            print ("No se ha detectado una clave de VirusTotal en la configuracion, revise el fichero .conf")
            return None
        vt = None
        try:
            vt =  VirusTotalPublicApi(key)
        except:
            print ("Hubo problemas con la clave de VT: " + key)
            return None
        
        result = {}    

        if data not in self.GLOBAL_IPS.keys():
            _analyzer=self.analyze_ip(vt, data)
            if _analyzer is not None:
                result = _analyzer
                self.GLOBAL_IPS[data] = _analyzer
        else:
            result = self.GLOBAL_IPS[data]
        
        return result
        
    def analyze_ip(self, vt, ip):
        print ("Analizando IP "+ip)
        result = {}
        ip_report = None
        try:
            ip_report = vt.get_ip_report(ip)   #get the VT IP report for this IP
        except:
            print ("API error: on ip " + ip)
            ip_report = None
        if ip_report is not None:
            if ip_report["response_code"] == 200:
                result ["country"] = ip_report["results"]["country"]
                detected_urls = ip_report["results"]["detected_urls"]
                total_pos = sum([u["positives"] for u in detected_urls])
                if total_pos > 0:
                    result ["threat"] = True
                else:
                    result ["threat"] = False
        return result