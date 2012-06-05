#!/usr/bin/python

from Harvester.Server import Server, cfgfiles

if __name__ == '__main__':
#    make_server()
    server = Server.load(*cfgfiles)
    server.run()
    