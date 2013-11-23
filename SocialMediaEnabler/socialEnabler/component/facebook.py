__author__ = 'mpetyx'

import tweepy
import json
import hashlib
import re
from couchbase import Couchbase
from tweepy.utils import import_simplejson
import time
from threading import Thread

from facepy import GraphAPI

#Define Database connection creds
server = "localhost"
port = 8091
admin_username = "dev"
admin_password = "123456dev"
bucket = "default"
cbucket = Couchbase.connect(host=server,port=port,bucket=bucket)

#Define filter terms
# filterTerms = [ "#sofa", "#bed", "white sofa", "#furniture", "#minimaldesign", "#couch", "#chair", "#table", "#desk", "#bookcase", "#fengshui", "furniture", "zen furniture", "feng shui furniture", "kitchen table", "leather sofa", "minimal style","aidima","ikea","homedeco","@designmilk","@decorandceramic","@molostudio","@apparatu"]




#stuff needed for url replacement - note:could also use entities from twitter json
urls = '(?: %s)' % '|'.join("""http https telnet gopher file wais
ftp""".split())
ltrs = r'\w'
gunk = r'/#~:.?+=&%@!\-'
punc = r'.:?\-'
any = "%(ltrs)s%(gunk)s%(punc)s" % { 'ltrs' : ltrs,
                                     'gunk' : gunk,
                                     'punc' : punc }

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
""" % {'urls' : urls,
           'any' : any,
           'punc' : punc }

url_re = re.compile(url, re.VERBOSE | re.MULTILINE)


def replace_url(text):
    withoutURL = url_re.sub('_URL',text)
    return withoutURL


access_token = "CAACEdEose0cBAMbkxbLoZCL86bpYPA4t2Mnrd2rOlIMI0mqZBaYlgNydtGZBS2kU47bwr6KYz7qmVjKdZCABns5Pe5y2AZANfqi82LmZCF909YrfaMEmFnrZCyMX5xvrOrRQZCSQSnyBXG5ZCSfrUE60ceI7lTtqKRPxyLAeOHUeFDVkIdR4QB3QK0hMBfYYALCoZD"
graph = GraphAPI(access_token)

feed = graph.get('/coca-cola?fields=feed.limit(30)')

feed = feed['feed']['data']

#pprint(feed)

for message in feed:
    try:
        text = message['message']
        text_no_url = replace_url(text)
        created_at = message['created_time']
        user_name=message['from']['name']
        user_name = 'facebook:' + user_name
        fbid = message['id']
        json_to_keep={"text":text,"text_no_url":text_no_url,"user_name":user_name,"created_at":created_at,"fb_id":fbid}
        data_md5 = hashlib.md5(json.dumps(message, sort_keys=True)).hexdigest()
        # print data_md5
        cbucket.set(data_md5, json_to_keep)
    except KeyError,e:
        continue





# def fbThread():
#     print "doing something"
#
# while True:
#     t = Thread(target=fbThread, args=())
#     time.sleep(5)
#     t.start()