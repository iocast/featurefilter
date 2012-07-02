'''
Created on July 2, 2012

@author: michel
'''
from twisted.test.test_threadable import threading


class JSFileWriter(threading.Thread):
    
    def __init__(self, file, key, value, image, lock):
        self.file = file
        self.lock = lock
        self.key = key
        self.value = value
        self.image = image
    
    def run(self):
        with self.lock:
            line = self.file.readline()
            seekpoint = self.file.tell()
            while line:
                
                if line.find("getSymbols : function() {") >= 0:
                    frw = open(file, 'r+b')
                    frw.seek(seekpoint, 0)
                    
                    frw.writelines("""\t\tthis.symbols.push(["%s", "%s", OpenLayers.Filter.Comparison.EQUAL_TO, this.path + "/%s"]);\n""" % (self.key, self.value, self.image))
                    
                    chars = self.file.readlines()
                    while chars:
                        frw.writelines(chars)
                        chars = self.file.readline()
                    
                    
                    frw.truncate()
                    frw.close()
                    break
                
                line = self.file.readline()
                seekpoint = self.file.tell()
                
            self.file.close()
                
    