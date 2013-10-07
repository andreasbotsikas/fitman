import tweepy
import json
import hashlib
from couchbase import Couchbase
from tweepy.utils import import_simplejson

#Define Database connection creds 
server = "localhost"
port = 8091
admin_username = "Administrator"
admin_password = "evidev123456"
bucket = "twitteroriginal"

#Twitter auth stuff
consumer_key = 'GqoGkLHXt0HtnRTiI3bQQ'
consumer_secret = 'IGb9DKUu51icAI1HrRAhB1P7Pjotni9z9utENrwPcU'
access_token_key = "1108878662-B8dlM4ALUMggmhvzmxXMVf4WGKywna7uosPKNUo"
access_token_secret = "xYVo8LnUoyqfUcK76MjNettKemW7mHXKvzybUx3q2c"

#Define filter terms
filterTerms = [ "#sofa", "#bed", "white sofa", "#furniture", "#minimaldesign", "#couch", "#chair", "#table", "#desk", "#bookcase", "#fengshui", "furniture", "zen furniture", "feng shui furniture", "kitchen table", "leather sofa", "minimal style","aidima","ikea","homedeco"]

json = import_simplejson()

cbucket = Couchbase.connect(host=server,port=port,username=admin_username,password=admin_password,bucket=bucket)
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
            #print 'Ran on_data'
            data_md5 = hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()
            cbucket.set(data_md5,json.loads(data))
            print(json.loads(data))


l = StreamListener()
streamer = tweepy.Stream(auth=auth1, listener=l, timeout=3000)
streamer.filter(track = filterTerms)