'''
Created on Oct 2, 2011

@author: michel
'''

import math

class CenterOfMass(object):
    '''
    Calculates the center of mass aka center of gravity or centroid
    '''
        
    @staticmethod
    def fromLatLon(points):
        '''
        Returns the center of mass from an lat lon array
        '''
        sumX = 0
        sumY = 0
        sumZ = 0
        
        for point in points[:]:
            sumX += CenterOfMass.getX(float(point['lat']),  float(point['lon']))
            sumY += CenterOfMass.getY(float(point['lat']),  float(point['lon']))
            sumZ += CenterOfMass.getZ(float(point['lat']))
        
        x = sumX / len(points)
        y = sumY / len(points)
        z = sumZ / len(points)
        
        return CenterOfMass.getLatLon(x, y, z)
            
    @staticmethod
    def getX(lat, lon):
        return math.cos(math.radians(lat)) * math.cos(math.radians(lon))
    
    @staticmethod
    def getY(lat, lon):
        return math.cos(math.radians(lat)) * math.sin(math.radians(lon))
    
    @staticmethod
    def getZ(lat):
        return math.sin(math.radians(lat))
    
    @staticmethod
    def getXYZ(lat, lon):
        x = CenterOfMass.getX(lat, lon)
        y = CenterOfMass.getY(lat, lon)
        z = CenterOfMass.getZ(lat)
        return (x,y,z)
    
    @staticmethod
    def getLatLon(x, y, z):
        lon = math.atan2(y, x)
        hyp = math.sqrt(x * x + y * y)
        lat = math.atan2(z, hyp)
        return (math.degrees(lat),math.degrees(lon))
        