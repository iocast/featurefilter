'''
Created on Oct 1, 2011

@author: michel
'''
import math
from FeatureFilter.Geometry.CenterOfMass import CenterOfMass

class MarkerCluster(object):
    ''' '''
    
    @staticmethod
    def cluster(point, bbox, size, radius):
        """
        bbox = min lat, min lon, max lat, max lon
        size = width height
        distance = in pixels
        """
        diag_pixels = math.sqrt(math.pow(float(size[0]), 2) + math.pow(float(size[1]), 2))
        diag_dist = MarkerCluster.getHaversineDistance(float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))
        
        points = point
                
        clustered = []
        while(len(points)):
            point1  = points.pop()
            cluster = []
            # Compare against all markers which are left.
            for point2 in points[:]:
                distance = MarkerCluster.getHaversineDistance(float(point1['lat']), float(point1['lon']), float(point2['lat']), float(point2['lon']))
                pixels = distance / diag_dist * diag_pixels
                # If two markers are closer than given distance remove
                # target marker from array and add it to cluster.
                if(pixels < radius):
                    #print("Distance between %s,%s and %s,%s is %d pixels.\n" % (point1['lat'], point1['lon'], point2['lat'], point2['lon'], pixels))
                    points.remove(point2)
                    cluster.append(point2)

            # If a marker has been added to cluster, add also the one
            # we were comparing to and remove the original from array.
            if(len(cluster) > 0):
                cluster.append(point1)
                clustered.append(cluster)
            else:
                clustered.append(point1)
        
        return clustered;
        
    @staticmethod
    def getHaversineDistance(lat1, lon1, lat2, lon2):
        latd = math.radians(float(lat2) - float(lat1))
        lond = math.radians(float(lon2) - float(lon1))
        
        
        a = math.sin(latd/2) * math.sin(latd/2) + math.cos(math.radians(float(lat1))) * math.cos(math.radians(float(lat2))) * math.sin(lond/2) * math.sin(lond/2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return 6371.0 * c

    @staticmethod
    def getCentroid(points):
        ''' returns the centroid '''
        lat, lon = CenterOfMass.fromLatLon(points)
        return {'lat':lat, 'lon':lon}
    