#!/usr/bin/python

import sys, os, time, socket
import ConfigParser
from web_request.handlers import wsgi, mod_python, cgi

from web_request.response import Response
from FeatureFilter.Service.Service import Service
from FeatureFilter.Algorithms.Clustering.MarkerCluster import MarkerCluster

from lxml import etree
from lxml import objectify
import json

# First, check explicit FS_CONFIG env var
if 'FS_CONFIG' in os.environ:
    cfgfiles = os.environ['FS_CONFIG'].split(",")

# Otherwise, make some guesses.
else:
    # Windows doesn't always do the 'working directory' check correctly.
    if sys.platform == 'win32':
        workingdir = os.path.abspath(os.path.join(os.getcwd(), os.path.dirname(sys.argv[0])))
        cfgfiles = (os.path.join(workingdir, "featurefilter.cfg"), os.path.join(workingdir,"..","featurefilter.cfg"))
    else:
        cfgfiles = ("featurefilter.cfg", os.path.join("..", "featurefilter.cfg"), "/etc/featurefilter.cfg")


class Server (object):
    ''' '''
       
    def __init__ (self, services, config = {}, processes = {}):
        self.services    = services
        self.config      = config
        self.processes   = processes
        
    def _loadFromSection (cls, config, section, **objargs):
        for opt in config.options(section):
            if opt != 'script' and opt != 'host' and opt != 'port' and opt != 'protocol':
                objargs[opt] = config.get(section, opt)
        
        return Service(config.get(section, 'script'),
                       config.get(section, 'host'),
                       config.get(section, 'port'),
                       config.get(section, 'protocol'),
                       **objargs)
        
    loadFromSection = classmethod(_loadFromSection)

    def _load (cls, *files):        
        parser = ConfigParser.ConfigParser()
        parser.read(files)
        
        config = {}
        if parser.has_section("configuration"):
            for key in parser.options("configuration"):
                config[key] = parser.get("configuration", key)

        processes = {}
        services = {}
        for section in parser.sections():
            if section == "configuration": continue
            else:
                services[section] = cls.loadFromSection(parser, section)
        
        return cls(services, config, processes)
    load = classmethod(_load)
    
    def dispatchRequest (self, base_path="", path_info="/", params={}, request_method = "GET", post_data = None,  accepts = ""):
        """Read in request data, and return a (content-type, response string) tuple. May
           raise an exception, which should be returned as a 500 error to the user."""  
        response_code = "200 OK"
        host = base_path
        path = path_info.split("/")
        
        service = None
        if params.has_key('server'):
            service = self.services[params['server']]
        else:
            service = self.services[path[len(path)-1]]
            
        # send data to harvester
        if self.config.has_key('harvester_host') and self.config.has_key('harvester_port'):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect((self.config['harvester_host'], int(self.config['harvester_port'])))
                sock.sendall("{\"params\":[" + str(json.dumps(params)) + "], \"post_data\":" + json.dumps(post_data) + "}")
                #received = sock.recv(1024)
            finally:
                sock.close()

        service.request(params=params, post_data=post_data, method=request_method)
        
        if params.has_key('clustering'):
            if params['clustering'].lower() == "false":
                return Response(data=service.getData(), content_type=service.getContentType(), headers=None, status_code=service.getStatusCode(), encoding='')
                               
        bbox = []
        if params.has_key('bbox'):
            bbox = params['bbox'].split(',')
        else:
            if len(post_data) > 0:
                parser = objectify.makeparser(remove_blank_text=True, ns_clean=True)
                dom = etree.XML(post_data, parser=parser)
                query = dom.xpath("//*[local-name() = 'BBOX']")
                if len(query) > 0:
                    bbox.extend(str(query[0].xpath("//*[local-name() = 'lowerCorner']")[0]).split(" "))
                    bbox.extend(str(query[0].xpath("//*[local-name() = 'upperCorner']")[0]).split(" "))
                    
        size = params['size'].split(',')
        
        clusterList = MarkerCluster.cluster(service.convertToPoints(params), bbox, size, 15)
        for cluster in clusterList:
            if isinstance(cluster, dict) == False:
                service.appendCentroid(MarkerCluster.getCentroid(cluster), cluster)

        reponse = Response(data=service.getContent(), content_type=service.getContentType(), headers=None, status_code=service.getStatusCode(), encoding='utf-8')
        return reponse 

theServer = None
lastRead = 0

def handler (apacheReq):
    global theServer
    if not theServer:
        options = apacheReq.get_options()
        cfgs    = cfgfiles
        if options.has_key("FeatureFilterConfig"):
            cfgs = (options["FeatureFilterConfig"],) + cfgs
        theServer = Server.load(*cfgs)
    return mod_python(theServer.dispatchRequest, apacheReq)

def wsgi_app (environ, start_response):
    global theServer, lastRead
    last = 0
    for cfg in cfgfiles:
        try:
            cfgTime = os.stat(cfg)[8]
            if cfgTime > last:
                last = cfgTime
        except:
            pass        
    if not theServer or last > lastRead:
        cfgs      = cfgfiles
        theServer = Server.load(*cfgs)
        lastRead = time.time()
        
    return wsgi(theServer.dispatchRequest, environ, start_response)


if __name__ == '__main__':
    service = Server.load(*cfgfiles)
    cgi(service)
