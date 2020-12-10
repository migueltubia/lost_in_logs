from Engine import TextEngine


class Fortigate(TextEngine):
    def __init__(self):
        super().__init__()

    def get_name(self):
        return "Fortigate"
        
    def get_description(self):
        return "Get Fortigate data"
    
    def get_pattern(self):
        return "%{DATA} itime=\"%{TIMESTAMP_ISO8601:time}\" %{DATA} action=\"%{DATA:action}\" %{DATA} sentbyte=%{NUMBER:sent_byte} rcvdbyte=%{NUMBER:rec_byte} %{DATA} srcport=%{NUMBER:src_port} dstport=%{NUMBER:dst_port} %{DATA} srcip=%{IP:src_ip} dstip=%{IP:dst_ip} %{DATA} app=\"%{DATA:application}\" %{DATA}"