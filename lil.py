import argparse
import sys
from colorama import Fore, Back, Style
from colorama import init
from importlib import import_module
from os.path import dirname, basename, isfile, join
import glob
import Configuration
import DB
import time

parser = argparse.ArgumentParser()
parser.add_argument('-e', '--engine', help='Engine to use')
parser.add_argument('-f', '--file', help='File to analyze')
parser.add_argument('-d', '--directory', help='Folder to analyze (all foles)')
parser.add_argument('-l', '--list', help='List modules', action='store_true')
parser.add_argument('-r', '--run', help='Run visualization engine')
parser.add_argument('-cn', '--clean_neo', help='Clean all connections and nodes data in NEO, REMOVE all the data in Neo4J Data Base', action='store_true')
parser.add_argument('-cd', '--clean_data', help='Clean all data inventory and management data', action='store_true')
args = parser.parse_args()

init(autoreset=True)

def loadEngines():
    modules = glob.glob("modules/" + join(dirname(__file__), "*.py"))
    engineNames = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
    engList = []
    for e in engineNames:
        engList.append(import_module('.' + e, package='modules'))
    return engList, engineNames

def loadAnalyzers():
    analyzers = glob.glob("analyzers/" + join(dirname(__file__), "*.py"))
    engineNames = [basename(f)[:-3] for f in analyzers if isfile(f) and not f.endswith('__init__.py')]
    engList = []
    for e in engineNames:
        engList.append(import_module('.' + e, package='analyzers'))
    return engList, engineNames

_intro = """
   __           _     _           __                 
  / /  ___  ___| |_  (_)_ __     / /  ___   __ _ ___ 
 / /  / _ \/ __| __| | | '_ \   / /  / _ \ / _` / __|
/ /__| (_) \__ \ |_  | | | | | / /__| (_) | (_| \__ \

\____/\___/|___/\__| |_|_| |_| \____/\___/ \__, |___/
                                           |___/     
"""
print (Fore.BLUE + _intro)

if not(args.engine and (args.file or args.directory)) and not(args.list or args.run) and (args.list and args.run):
    print("AYUDA")
    sys.exit("¿¿En serio Jorge??")

print("Lost in logs se está inicializando...")

engines, engineNames = loadEngines()
analyzers, analyzersNames = loadAnalyzers()

if args.list:
    for i, x in enumerate(engines):
        try:
            engineClass = getattr(x, engineNames[i])
            engineObject = engineClass()
            print (Fore.LIGHTRED_EX + engineObject.module_name + Fore.MAGENTA + " -- "+ Fore.GREEN + engineObject.description)
            print ()
        except Exception as e:
            print(Fore.LIGHTRED_EX + "Error al cargar " + engineNames[i] + Style.RESET_ALL)
            print(Fore.LIGHTRED_EX + str(e) + Style.RESET_ALL)
    sys.exit("Lost in logs done")

if args.run:
    sys.exit("Lost in logs done")

if args.clean_neo:
    DB.cleanData()
    sys.exit("All nodes in Neo4J removed")

directory = None
file = None
engine = None

if args.directory:
    directory=args.directory
    if directory == "":
        directory = None
if args.file:
    file=args.file
    if file == "":
        file = None
if args.engine:
    engine=args.engine
    if engine == "":
        engine = None

nodes = []
ips=[]

for i, x in enumerate(engines):
    if engine==engineNames[i]:
        print ("Ejecutando engine " + engine)
        try:
            engineClass = getattr(x, engineNames[i])
            engineObject = engineClass()
            if file is None:
                 files = glob.glob(directory+"/" + join(dirname(__file__)))
                 fileNames = [basename(f)[:-3] for f in files if isfile(f)]
                 for _file in fileNames:
                    _nodes = engineObject._run(_file)
                    nodes += _nodes
                    ips += engineObject.IPS
            else:
                nodes = engineObject._run(file)
                ips = engineObject.IPS
        except Exception as e:
            print(Fore.LIGHTRED_EX + "Error al cargar " + engineNames[i] + Style.RESET_ALL)
            print(Fore.LIGHTRED_EX + str(e) + Style.RESET_ALL)

if len(nodes) == 0:
    print (Fore.RED + "No se ha podido recuperar ningún dato")
    sys.exit()

DB.saveData(nodes)

for _ip in ips:
    _node_analyzer = {}
    for i, x in enumerate(analyzers):
        print ("Ejecutando analizador " + analyzersNames[i])
        try:
            analyzerClass = getattr(x, analyzersNames[i])
            analyzerObject = analyzerClass()
            result = analyzerObject._run(_ip)
            _node_analyzer[analyzersNames[i]] = result
        except Exception as e:
            print(Fore.LIGHTRED_EX + "Error al cargar " + analyzersNames[i] + Style.RESET_ALL)
            print(Fore.LIGHTRED_EX + str(e) + Style.RESET_ALL)
    DB.saveAnalyzers(_ip, _node_analyzer)

