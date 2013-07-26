import tweepy
import json
import hashlib
import couchbase
from tweepy.utils import import_simplejson

#Define Database connection creds 
server = "localhost:8091"
admin_username = "mpetyx"
admin_password = "galois"

#Twitter auth stuff
consumer_key = 'tlroHIz4mz32PE9YbqRx2A'
consumer_secret = 'eOFSXMTpJaCGkQ5tG7MwfNFxHdTLGeiYE3rfkK6Q'
access_token_key = "95257276-VuvdqXZV4WXyYMqDjkmEOuQS7zB2DavY1zu6D0V9s"
access_token_secret = "zmnKLusHGkTJzu2lkzVSJQdFBu4EBavjOfUB3x8eEA"

#Define filter terms
filterTerms = ['bigdata', 'couchbase', 'nosql', 'DataWeek', 'CouchConf']

json = import_simplejson()
try:
	cbsclient = couchbase.Server(server, admin_username, admin_password); 
except:
	print "Cannot find Couchbase Server ... Exiting\n"
	print "----_Stack Trace_-----\n"
	raise

#Couchbase is found here so now try to create a bucket for twitter
try:
	cbsclient.create('twitter', ram_quota_mb=200, replica=1)
except:
	pass

#Try to use the twitter bucket or else switch to use default bucket
try:
	cbucket = cbsclient['twitter']
	print "Using twitter bucket"
except:
	cbucket = cbsclient['default']
	print "Using default bucket"

auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth1.set_access_token(access_token_key, access_token_secret)

class StreamListener(tweepy.StreamListener):
    json = import_simplejson()
    
    def on_status(self, tweet):
        print 'Ran on_status'

    def on_error(self, status_code):
        return False

    def on_data(self, data):
        if data[0].isdigit():
            pass
        else:
	    data_md5 = hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()
	    cbucket.set(data_md5,0,0,data)
            print(json.loads(data))


l = StreamListener()
streamer = tweepy.Stream(auth=auth1, listener=l)
streamer.filter(track = filterTerms)