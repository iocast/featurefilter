'''
Created on Oct 1, 2011

@author: michel
'''
import unittest
from FeatureFilter.Algorithms.Clustering.MarkerCluster import MarkerCluster

class MarkerClusterTestCase(unittest.TestCase):
    clustor = None
    points = [
        {'id' : 'marker_1',
         'lat' : 59.441193,
         'lon' : 24.729494},
        {'id' : 'marker_2',
         'lat' : 59.432365,
         'lon' : 24.742992},
        {'id' : 'marker_3',
         'lat' : 59.431602,
         'lon' : 24.757563},
        {'id' : 'marker_4',
         'lat' : 59.437843,
         'lon' : 24.765759},
        {'id' : 'marker_5',
         'lat' : 59.439644,
         'lon' : 24.779041},
        {'id' : 'marker_6',
         'lat' : 59.434776,
         'lon' : 24.756681}
    ]
    
    def setUp(self):
        self.clustor = MarkerCluster()
    
    def testCluster(self):
        result = [[{'lat': 59.431602, 'lon': 24.757563, 'id': 'marker_3'}, {'lat': 59.437843, 'lon': 24.765759, 'id': 'marker_4'}, {'lat': 59.434776, 'lon': 24.756681, 'id': 'marker_6'}], {'lat': 59.439644, 'lon': 24.779041, 'id': 'marker_5'}, {'lat': 59.432365, 'lon': 24.742992, 'id': 'marker_2'}, {'lat': 59.441193, 'lon': 24.729494, 'id': 'marker_1'}]
        
        clustered = self.clustor.cluster(self.points, 20, 11)
        self.assertItemsEqual(result, clustered, "clustered array has not the same items")
    
    def testCentroid(self):
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()