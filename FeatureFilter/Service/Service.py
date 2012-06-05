'''
Created on Sep 29, 2011

@author: michel
'''
import urllib
import urllib2
from lxml import etree
from copy import deepcopy, copy

class Service(object):
    data = None
    header = None
    dom = None
    tmplNode = None

    def __init__(self, script, host, port='80', protocol='http', **kwargs):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.script = script
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def request(self, params={}, post_data=None, method="get"):
        self.dom = None
        
        request= urllib2.Request(self.getURL()+'?'+urllib.urlencode(params))
        
        if post_data:
            request.add_data(post_data)
            
        response = urllib2.urlopen(request)
        
        self.data = response.read()
        self.header = response.info()
        self.status = response.getcode()
    
    def convertToPoints(self, params):
        points = []
        if self.dom == None:
            try:
                self.dom = etree.fromstring(self.data)
                if len(self.dom) > 0:
                    self.tmplNode = deepcopy(self.dom[0])
                else:
                    return points
            except etree.ParseError:
                return points
        
        for feature in self.dom.xpath('''//*[local-name() = '%s']''' % params['typename'], namespaces = self.dom.nsmap):
            coordinate = feature.xpath('''.//*[local-name() = 'coordinates']''', namespaces = self.dom.nsmap)[0]
            coordinates = coordinate.text.split(coordinate.attrib['cs'])
            points.append({'id':feature.attrib['fid'],
                           'lat':coordinates[0],
                           'lon':coordinates[1]})
        
        return points
    
    def removeById(self, id):
        if self.dom == None:
            self.dom = etree.fromstring(self.data)
            self.tmplNode = deepcopy(self.dom[0])
        
        features = self.dom.xpath('''//*[@fid="%s"]''' % id, namespaces=self.dom.nsmap)
        for feature in features:
            feature.getparent().getparent().remove(feature.getparent())
    
    def getById(self, id):
        if self.dom == None:
            self.dom = etree.fromstring(self.data)
            self.tmplNode = deepcopy(self.dom[0])
        
        features = self.dom.xpath('''//*[@fid="%s"]''' % id, namespaces=self.dom.nsmap)
        if len(features) > 0:
            return features[0]
        return None
    
    def append(self, feature):
        node = deepcopy(self.tmplNode)
        featureCopy = feature.copy()
        nsmap = {}
        nskey = ""
        nsvalue = ""
        child = None
        
        if 'id' in feature:
            node[0].attrib['fid'] = feature['id']
            del featureCopy['id']
        
        for child in node[0]:
            localname = child.xpath('local-name()')
            if localname == 'Point':
                child[0].text = str(feature['lat']) + child[0].attrib['cs'] + str(feature['lon'])
                del featureCopy['lat']
                del featureCopy['lon']
            else:
                if localname in feature:
                    child.text = feature[localname]
                    del featureCopy[localname]
                else:
                    child.text = ''
                    
        if(child != None):
            nsmap = copy(child).nsmap
        else:
            nsmap = copy(self.tmplNode[0]).nsmap
        for nskey, nsvalue in nsmap.items():
            break;
        
        # add elements not found in feature dom
        for key in featureCopy:
            if isinstance(featureCopy[key], list) == True:
                if key == self.cluster_feature_label:
                    element = etree.Element('{%s}%s' % (nsvalue, key), nsmap=nsmap)
                    for value in featureCopy[key]:
                        item = etree.Element('{%s}%s' % (nsvalue, self.cluster_item_label), nsmap=nsmap)
                        item.text = str(value)
                        element.append(item)
            else:
                element = etree.Element('{%s}%s' % (nsvalue, key), nsmap=nsmap)
                element.text = str(featureCopy[key])
            
            node[0].append(element)
        
        self.dom.append(node)
    

    def appendCentroid(self, centroid, cluster):
        centroid['id'] = ''
        centroid['name'] = ''
        
        if hasattr(self, 'cluster_indicator_label'):
            centroid[self.cluster_indicator_label] = "true"
        if hasattr(self, 'cluster_amount_label'):
            centroid[self.cluster_amount_label] = len(cluster)
        
        if hasattr(self, 'cluster_feature_label'):
            if hasattr(self, 'cluster_item_delimiter'):
                centroid[self.cluster_feature_label] = ""
            else:
                centroid[self.cluster_feature_label] = []
        
        for point in cluster:
            if hasattr(self, 'cluster_feature_list'):
                if self.cluster_feature_list:
                    if hasattr(self, 'cluster_item_delimiter'):
                        centroid[self.cluster_feature_label] += self.cluster_item_delimiter + str(point['id'])
                    else:
                        centroid[self.cluster_feature_label].append(point['id'])
            
            self.removeById(point['id'])
        
        self.append(centroid)    
                
    def getContent(self):
        return etree.tostring(self.dom)
    
    def getData(self):
        return self.data
    
    def getContentType(self):
        return self.header['Content-Type']
    
    def getSize(self):
        return self.header['Content-Length']
    
    def getStatusCode(self):
        return self.status
    
    def getURL(self):
        return self.protocol + '://' + self.host + ':' + self.port + self.script
        