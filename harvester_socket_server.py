#!/usr/bin/python

__author__  = "Michel Ott"
__version__ = "0.1"
__license__ = "???"
__copyright__ = "???"

from Harvester.Server import Server, cfgfiles

if __name__ == '__main__':
    server = Server.load(*cfgfiles)
    server.run()
    