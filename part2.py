import csv
import json
import math
import decimal
import random
import copy
import sys
import re

#To represent one tweet
class tweet(object):

    def __init__(self, args):
    	self.text = args.get('text', '') #Get text
    	#Clean text data
        self.text = re.sub('^(RT @.+?: )+', '', self.text)
        self.text = re.sub('#\w+', '', self.text)
        self.text = re.sub("[^\w ]", '', self.text)
        self.words = self.text.split()
        self.id = str(args.get('id', '')) #Get ID

  
    def __repr__(self):
        return self.id + " : " + self.text

def readtweetdata(file):
    indata = []
    for line in open(file, 'r'):
        data = json.loads(line)
        cleaneddata = dict( (key, value) for key, value in data.items() if key in ('text', 'id') )
        dtweet = tweet({'id' : cleaneddata['id'], 'text' : cleaneddata['text'] })
        indata.append(dtweet)
    return indata

# Computes Jaccard distance between two given sets
def Jaccarddist(A, B):
    setA = set(A.words)
    setB = set(B.words)
    return 1 - ( len(setA.intersection(setB)) / float( len(setA.union(setB)) ) ) 


#Performing K-Means Algorithm
class KMeans(object):

    def __init__(self, args):
        self.K = int(args.get('K', 0))
        self.data = args.get('data', None)
        self.iseeds = args.get('iseeds', None)
        self.itermax = args.get('itermax', 25)
        self.cutoff = args.get('cutoff', 1) #Convergence Cutoff
        self.clusters = []

    # executes the k-means algorithm on the given data nodes
    def execute(self):
        self.init_cent()

        count, change = 0, decimal.Decimal('Infinity')
        while self.converge(count, change) != True:


            clusterLists = [ [] for i in self.clusters ]

            for tweet in self.data:
                CI = -1		#Cluster Index
                mindist = decimal.Decimal('Infinity')

                for i in range(len(self.clusters)):
                    distance = Jaccarddist(tweet, self.clusters[i].centroid)
                    if mindist > distance:
                        mindist = distance
                        CI = i

                if CI != -1:
                    clusterLists[CI].append(tweet)

            change = 0.0
            # Update clusters with the new set of nodes and compute
            # the new centroid for them.
            for i in range(len(self.clusters)):
                self.clusters[i].setnodes(clusterLists[i])
                
                oldcent = self.clusters[i].centroid
                self.clusters[i].newclustercent()

                change = max( change, Jaccarddist(oldcent, self.clusters[i].centroid) )

            count += 1

    
	# Returns the Tweet object for the given ID
    def getData(self, ID):
        for tweet in self.data:
            if tweet.id == ID:
                return tweet

        return None

    # Loads the centroids given in the seeds file as the initial
    # centroids for the 'K' clusters.
    def init_cent(self):
        IDList = []
        for ID in open(self.iseeds, 'r'):
            ID = re.sub('[\s,]+', '', ID)
            IDList.append(ID)

        kSamples = random.sample(IDList, self.K)
        for sample in kSamples:
            tCluster = Cluster({
                'centroid' : self.getData(sample)
            })
            self.clusters.append(tCluster)

    # Checks convergence
    def converge(self, count, change):
        if change <= self.cutoff:
            return True

        if count > self.itermax:
            return True

        return False

    # Prints clusters in the below format
    # Cluster-id    csv of nodes
    def writeOutput(self, resultsoutput=None):
        CI = 1
        for cluster in self.clusters:
            if resultsoutput == None:
                #print "%d\t%s" % (CI, cluster)
                print "%d:" % CI
                for point in cluster.nodes:
                    print point.text
            else:
                resultsoutput.write( "%d\t%s\n" % (CI, cluster) )
            CI += 1

    # Calculates the Sum of squared error
    def calculatesse(self):
        SSE = 0.0
        for i in range(self.K):
            for node in self.clusters[i].nodes:
                SSE += Jaccarddist(self.clusters[i].centroid, node)**2
        return SSE

# This class represents one cluster
class Cluster(object):
    #Nodes represent the tweets within the cluster
    def __init__(self, args):
        self.centroid = args.get('centroid', None)
        self.nodes = args.get('nodes', None)

    def setnodes(self, nodes):
        self.nodes = nodes

    def newclustercent(self):
       
        totalnodes = len(self.nodes)
        if totalnodes != 0:
            minSum, tminsum = decimal.Decimal('Infinity'), None

            for i in range(totalnodes):
                dist = 0.0
                A = self.nodes[i]
                for j in range(totalnodes):
                    dist += Jaccarddist(A, self.nodes[j])

                if dist < minSum:
                    minSum = dist
                    tminsum = A

            self.centroid = tminsum

    def __repr__(self):
        return ",".join( str(tweet.id) for tweet in self.nodes )


#Main STARTS HERE

#Loading the arguments
K = sys.argv[1]
iseeds = sys.argv[2]
tweetrawdata = sys.argv[3]
results = sys.argv[4]

rawdata = readtweetdata(tweetrawdata)

kmeans = KMeans({'K' : K, 'data' : rawdata, 'iseeds' : iseeds })

kmeans.execute()
resultsoutput = open(results, 'w')
kmeans.writeOutput(resultsoutput)

sse = kmeans.calculatesse()
# Print SSE to file
resultsoutput.write("SSE : %f\n"  % sse)

print "SSE: ", sse
#Main ENDS HERE