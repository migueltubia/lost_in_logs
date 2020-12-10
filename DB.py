import Configuration
from colorama import Fore, Back, Style
from neo4j import GraphDatabase
from string import Template

Q_FIND_DEVICE = Template("MATCH (d:Device) WHERE d.ip = '${ip}' RETURN d")
Q_CREATE_DEVICE = Template("CREATE (d:Device { ip: '${ip}' }) RETURN d")
Q_CREATE_RELATION = Template ("MATCH (src:Device), (dst:Device) WHERE src.ip = '${src}' AND dst.ip='${dst}' CREATE (src)-[r:CONNECTED {time:'${time}', action:'${action}', sentbyte:${sentbyte}, rcvdbyte:${rcvdbyte}, src_port:${src_port}, dst_port:${dst_port}, application:'${application}', source:'${source}'}]->(dst)")
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
        src = getDevice(srcip)
        if src is None:
            src = createDevice(srcip)
        dst = getDevice(dstip)
        if dst is None:
            dst = createDevice(dstip)
        createRelation(srcip, dstip, d["time"], d["action"], d["sent_byte"], d["rec_byte"], d["src_port"], d["dst_port"], d["application"], d["source"])

def createRelation(src, dst, time, action, sentbyte, rcvdbyte, src_port, dst_port, application, source):
    with graph.session() as session:
        nodes = session.run(Q_CREATE_RELATION.substitute(src=src, dst=dst, time=time, action=action, sentbyte=sentbyte, rcvdbyte=rcvdbyte, src_port=src_port, dst_port=dst_port, application=application, source=source))

def createDevice(ip):
    node = None
    with graph.session() as session:
        nodes = session.run(Q_CREATE_DEVICE.substitute(ip=ip))
        for _node in nodes:
            node = _node
    return node

def getDevice(ip):
    node = None
    with graph.session() as session:
        nodes = session.run(Q_FIND_DEVICE.substitute(ip=ip))
        for _node in nodes:
            node = _node
    return node
    
def saveAnalyzers(ip, analyzers):
    with graph.session() as session:
        _n = session.run(Q_SAVE_ANALYZER.substitute(ip=ip, analyzers=analyzers))