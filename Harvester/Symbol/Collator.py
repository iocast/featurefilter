'''
Created on Mar 5, 2012

@author: michel
'''
from unicodedata import normalize
import os, urllib, re
from lxml import etree
import urllib2
from twisted.test.test_threadable import threading

class Collator(object):
    
    __config = None
    __servers = []
    __extensions = []
    __params = []
    __post_data = ""
    
    def __init__(self, config, params, post_data):
        self.__config = config
        self.__servers = self.__config['servers'].split('\n')
        self.__extensions = self.__config['extensions'].split(',')
        self.__params = params
        self.__post_data = post_data
    
    def check(self):
        missing = []
        dom = None
        
        if self.__params.has_key('filter'):
            dom = etree.fromstring(self.__params['filter'])
        elif len(self.__post_data) > 0:
            dom = etree.fromstring(self.__post_data)
        
        for property_node in dom.xpath('''//*[local-name() = 'PropertyName']''', namespaces = dom.nsmap):
            prop = str(property_node.text)
            value = str(property_node.getnext().text)
            
            #check on file system if file exists
            for extension in self.__extensions:
                path = re.sub(r'\s+', '', 'images/symbols/%s_%s.%s' % (prop, value, extension))
                if os.path.isfile(path) <> True:
            
                    path = re.sub(r'\s+', '', 'images/symbols/%s_%s.%s' % (prop.lower(), value, extension))
                    if os.path.isfile(path) <> True:
                
                        path = re.sub(r'\s+', '', 'images/symbols/%s_%s.%s' % (prop, value.lower(), extension))
                        if os.path.isfile(path) <> True:
                            missing.append([prop, value])
        
        return missing
            
    def downloadSymbols(self, list):
        for server in self.__servers:
            for index, (prop, value) in enumerate(list):
                for extension in self.__extensions:
                    extension = extension.strip()
                    
                    url = re.sub(r'\s+', '', server + prop + "." + extension)
                    image = urllib.URLopener()
                    try:
                        image.retrieve(url, re.sub(r'\s', '', 'images/symbols/%s_%s.%s' % (prop, value, extension)))
                        self.addSymbolToJavaScript('js/Symbols.js', prop, value, 'images/symbols/%s_%s.%s' % (prop, value, extension))
                        list.pop(index)
                        continue
                    except IOError:
                        ''' '''
                    url = re.sub(r'\s+', '', server + value + "." + extension)
                    image = urllib.URLopener()
                    try:
                        image.retrieve(url, re.sub(r'\s', '', 'images/symbols/%s_%s.%s' % (prop, value, extension)))
                        self.addSymbolToJavaScript('js/Symbols.js', prop, value, 'images/symbols/%s_%s.%s' % (prop, value, extension))
                        list.pop(index)
                    except IOError:
                        ''' '''
    
    def addSymbolToJavaScript(self, file, key, value, img):
        lock = threading.Lock()
        fro = open(file, 'rb')
        
        jsFileWriter = JSFileWriter(fro, key, value, img, lock)
        