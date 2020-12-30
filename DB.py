import Configuration
from colorama import Fore, Back, Style
from neo4j import GraphDatabase
from string import Template

Q_FIND_DEVICE = Template("MATCH (d:Device) WHERE d.name = '${name}' RETURN d")
Q_CREATE_DEVICE = Template("CREATE (d:Device { name:  '${name}', ip: '${ip}' }) RETURN d")
Q_CREATE_RELATION = Template ("MATCH (src:Device), (dst:Device) WHERE src.name = '${src}' AND dst.name='${dst}' CREATE (src)-[r:CONNECTED {time:'${time}', action:'${action}', sentbyte:${sentbyte}, rcvdbyte:${rcvdbyte}, src_port:${src_port}, dst_port:${dst_port}, application:'${application}', source:'${source}'}]->(dst)")
Q_CLEAN = "MATCH (n) DETACH DELETE n"
Q_SAVE_ANALYZER = Template ("MATCH (d { ip: '${ip}' }) SET d.analyzers=\"${analyzers}\" return d")



graph = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "1234"))

def cleanData():
    with graph.session() as session:
        nodes = session.run(Q_CLEAN)

def saveData(data):
    nodes = []
    for d in data:
        srcip=d["src_ip"]
        dstip=d["dst_ip"]
        srcname=d["src_name"]
        dstname=d["dst_name"]
        src = getDevice(srcname)
        if src is None:
            src = createDevice(srcname, srcip)
        dst = getDevice(dstname)
        if dst is None:
            dst = createDevice(dstname, dstip)
        _time = d["time"] if "time" in d.keys() else ""
        _action = d["action"] if "action" in d.keys() else ""
        _sent_byte = d["sent_byte"] if "sent_byte" in d.keys() else 0
        _rec_byte = d["rec_byte"] if "rec_byte" in d.keys() else 0
        _src_port = d["src_port"] if "src_port" in d.keys() else 0
        _dst_port = d["dst_port"] if "dst_port" in d.keys() else 0
        _application = d["application"] if "application" in d.keys() else ""
        _source = d["source"] if "source" in d.keys() else ""
        createRelation(srcname, dstname, _time, _action, _sent_byte, _rec_byte, _src_port, _dst_port, _application, _source)

def createRelation(src, dst, time, action, sentbyte, rcvdbyte, src_port, dst_port, application, source):
    with graph.session() as session:
        nodes = session.run(Q_CREATE_RELATION.substitute(src=src, dst=dst, time=time, action=action, sentbyte=sentbyte, rcvdbyte=rcvdbyte, src_port=src_port, dst_port=dst_port, application=application, source=source))

def createDevice(name, ip):
    node = None
    with graph.session() as session:
        nodes = session.run(Q_CREATE_DEVICE.substitute(name=name, ip=ip))
        for _node in nodes:
            node = _node
    return node

def getDevice(name):
    node = None
    with graph.session() as session:
        nodes = session.run(Q_FIND_DEVICE.substitute(name=name))
        for _node in nodes:
            node = _node
    return node
    
def saveAnalyzers(ip, analyzers):
    with graph.session() as session:
        _n = session.run(Q_SAVE_ANALYZER.substitute(ip=ip, analyzers=analyzers))