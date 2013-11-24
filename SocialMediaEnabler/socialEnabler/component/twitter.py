import json
import hashlib
import re

import tweepy
from couchbase import Couchbase
from tweepy.utils import import_simplejson


#stuff needed for url replacement - note:could also use entities from twitter json
urls = '(?: %s)' % '|'.join("""http https telnet gopher file wais
ftp""".split())
ltrs = r'\w'
gunk = r'/#~:.?+=&%@!\-'
punc = r'.:?\-'
any = "%(ltrs)s%(gunk)s%(punc)s" % {'ltrs': ltrs,
                                    'gunk': gunk,
                                    'punc': punc}

url = r"""
\b # start at word boundary
%(urls)s : # need resource and a colon
[%(any)s] +? # followed by one or more
# of any valid character, but
# be conservative and take only
# what you need to....
(?= # look-ahead non-consumptive assertion
[%(punc)s]* # either 0 or more punctuation
(?: [^%(any)s] # followed by a non-url char
| # or end of the string
$
)
)
""" % {'urls': urls,
       'any': any,
       'punc': punc}

url_re = re.compile(url, re.VERBOSE | re.MULTILINE)


def replace_url(text):
    withoutURL = url_re.sub('_URL', text)
    return withoutURL

#Define Database connection creds
server = "localhost"
port = 8091
admin_username = "dev"
admin_password = "123456dev"
bucket = "default"

#Twitter auth stuff
consumer_key = 'GqoGkLHXt0HtnRTiI3bQQ'
consumer_secret = 'IGb9DKUu51icAI1HrRAhB1P7Pjotni9z9utENrwPcU'
access_token_key = "1108878662-B8dlM4ALUMggmhvzmxXMVf4WGKywna7uosPKNUo"
access_token_secret = "xYVo8LnUoyqfUcK76MjNettKemW7mHXKvzybUx3q2c"

#Define filter terms
filterTerms = ["#sofa", "#bed", "white sofa", "#furniture", "#minimaldesign", "#couch", "#chair", "#table", "#desk",
               "#bookcase", "#fengshui", "furniture", "zen furniture", "feng shui furniture", "kitchen table",
               "leather sofa", "minimal style", "aidima", "ikea", "homedeco", "@designmilk", "@decorandceramic",
               "@molostudio", "@apparatu"]

json = import_simplejson()

cbucket = Couchbase.connect(host=server, port=port, bucket=bucket)
auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth1.set_access_token(access_token_key, access_token_secret)


class StreamListener(tweepy.StreamListener):
    json = import_simplejson()

    def on_status(self, tweet):
        #print 'Ran on_status'
        pass

    def on_error(self, status_code):
        return False

    def on_data(self, data):
        if data[0].isdigit():
            pass
        else:
            #print 'Ran on_data'
            data_md5 = hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()
            #cbucket.set(data_md5,json.loads(data))
            json_tweet = json.loads(data)
            fields_wanted = {"created_at", "text", "lang", "retweet_count", "id", "retweeted", "entities"}
            text = json_tweet["text"]
            json_to_keep = {k: json_tweet[k] for k in fields_wanted}
            text_no_url = replace_url(json_tweet["text"])
            json_to_keep["text_no_url"] = text_no_url
            user_name = json_tweet["user"]["name"]
            user_name = 'twitter:' + user_name
            json_to_keep["user_name"] = user_name
            user_screen_name = json_tweet["user"]["screen_name"]
            user_screen_name = 'twitter:' + user_screen_name
            json_to_keep["user_screen_name"] = user_screen_name
            json_to_keep["senti_tag"] = "neutral"
            cbucket.set(data_md5, json_to_keep)

            if json_tweet["lang"]:
                language = json_tweet["lang"]
                if language == 'en':
                    result_file = open("./files/%s" % data_md5, "w")
                    # result_file.write(data_md5)
                    # result_file.write("\n")
                    # print text_no_url
                    result_file.write(str(text_no_url.encode('utf-8')))
                    result_file.close()


l = StreamListener()
streamer = tweepy.Stream(auth=auth1, listener=l, timeout=3000)
streamer.filter(track=filterTerms)
