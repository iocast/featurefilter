'''
Created on Apr 2, 2012

@author: michel
'''

import os, sys
import ConfigParser
import SocketServer
import threading
import simplejson
import socket
from Harvester.Symbol.Collator import Collator

# First, check explicit FS_CONFIG env var
if 'FS_CONFIG' in os.environ:
    cfgfiles = os.environ['FS_CONFIG'].split(",")

# Otherwise, make some guesses.
else:
    # Windows doesn't always do the 'working directory' check correctly.
    if sys.platform == 'win32':
        workingdir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
        cfgfiles = (os.path.join(workingdir, "harvester.cfg"), os.path.join(workingdir,"..","harvester.cfg"))
    else:
        cfgfiles = ("harvester.cfg", os.path.join("..", "harvester.cfg"), "/etc/harvester.cfg")

def internal_server_error(environ, start_response):
    response = '<h1>Internal Server Error</h1>'.encode('utf-8')
    start_response(b'500 INTERNAL SERVER ERROR', [
        ('Content-Type', 'text/html; charset=utf-8'),
        ('Content-Length', str(len(response)))
    ])
    return [response]

class Server(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
#class Server(SocketServer.ForkingMixIn, SocketServer.TCPServer):
    _config = {}
    _processes = {}
    _sections = {}
    
    def __init__(self, sections = {}, config = {}, processes = {}):
        self._config = config
        self._processes = processes
        self._sections = sections
        
        SocketServer.TCPServer.__init__(self, (self._config['host'], int(self._config['port'])), TCPRequestHandler)
        
    def _load(cls, *files):
        parser = ConfigParser.ConfigParser()
        parser.read(files)
        
        config = {}
        if parser.has_section("configuration"):
            for key in parser.options("configuration"):
                config[key] = parser.get("configuration", key)
        
        processes = {}
        sections = {}
        for name in parser.sections():
            if name == "configuration": continue
            else:
                section = {}
                for key in parser.options(name):
                    section[key] = parser.get(name, key)
                sections[name] = section
        
        return cls(sections, config, processes)
    load = classmethod(_load)
    
    def run(self):
        server_thread = threading.Thread(target=self.serve_forever)
        server_thread.setDaemon(True)
        server_thread.allow_reuse_address = True
        server_thread.start()
        self.serve_forever()
    
    
class TCPRequestHandler(SocketServer.BaseRequestHandler):    
    def handle(self):
        #sys.path.append("/home/michel/.eclipse/org.eclipse.platform_3.5.0_155965261/plugins/org.python.pydev.debug_2.2.2.2011082312/pysrc/")
        #import pydevd; pydevd.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)
        
        self.request.settimeout(None)
        data = self.request.recv(int(self.server._config['size']))
        self.request.settimeout(2)
        while 1:
            line = ""
            try:
                line = self.request.recv(int(self.server._config['size']))
            except socket.timeout:
                break

            if line == "":
                break

            data += line
        
            
        obj = simplejson.loads(data)
        
        collator = Collator(self.server._sections["symbols"], obj["params"][0], obj["post_data"])
        notFound = collator.check()
        if len(notFound) > 0:
            collator.downloadSymbols(notFound)
