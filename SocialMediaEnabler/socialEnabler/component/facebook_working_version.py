'''
Created on Dec 20, 2013

@author: Evmorfia
'''
from facepy import GraphAPI
#from pprint import pprint
import re
import os
import hashlib
import json
import datetime
from couchbase import Couchbase

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

def find_url(text):
    return re.findall(url_re,text)

def replace_multichars(text):
    text = re.sub('aa+','aa',text)
    text = re.sub('bb+','bb',text)
    text = re.sub('cc+','cc',text)
    text = re.sub('dd+','dd',text)
    text = re.sub('ee+','ee',text)
    text = re.sub('ff+','ff',text)
    text = re.sub('gg+','gg',text)
    text = re.sub('hh+','hh',text)
    text = re.sub('ii+','ii',text)
    text = re.sub('jj+','jj',text)
    text = re.sub('kk+','kk',text)
    text = re.sub('ll+','ll',text)
    text = re.sub('mm+','mm',text)
    text = re.sub('nn+','nn',text)
    text = re.sub('oo+','oo',text)
    text = re.sub('pp+','pp',text)
    text = re.sub('qq+','qq',text)
    text = re.sub('rr+','rr',text)
    text = re.sub('ss+','ss',text)
    text = re.sub('tt+','tt',text)
    text = re.sub('uu+','uu',text)
    text = re.sub('vv+','vv',text)
    text = re.sub('ww+','ww',text)
    text = re.sub('xx+','xx',text)
    text = re.sub('yy+','yy',text)
    text = re.sub('zz+','zz',text)
    return text

def parse_comment(page_name,comment):
    json_to_keep = fix_json_format("FB_CMT "+comment['message'], comment['created_time'], page_name+":"+comment['from']['name'], comment['id'])
    return json_to_keep
#     print comment['message'].encode('utf-8') # note utf-8 needed
#     print comment['created_time']
#     print comment['from']['name'].encode('utf-8')
#     print comment['id']

def parse_post(page_name,message):
    json_to_keep = fix_json_format(message['message'], message['created_time'], page_name+":"+message['from']['name'], message['id'])
    if 'full_picture' in message:
        #print message['full_picture']
        json_to_keep["entities"]={"media":[{"media_url_https":message['full_picture']}]}
        #print json_to_keep
    #print message['full_picture']
    return json_to_keep
#     print message['message'].encode('utf-8')
#     print message['from']['name'].encode('utf-8')
#     print message['created_time']
#     print message['id']

def fix_json_format(text,date,username,pid):
    text_no_url = text.lower()
    text_no_url = replace_multichars(text_no_url)
    text_no_url = replace_url(text_no_url)
    username = "facebook:"+username
    json_to_keep = {'text_no_url':text_no_url,'fbid':pid,'created_at':datetime.datetime.strptime(date,'%Y-%m-%dT%H:%M:%S+0000').strftime('%a %b %d %H:%M:%S +0000 %Y'),'text':text, 'user_screen_name':username,'senti_tag':"neutral",'social_source':'facebook'}
    return json_to_keep

def connectToDb():
    #Define Database connection creds
    server = "localhost"
    port = 8091
    admin_username = ""
    admin_password = ""
    bucket = "default"
    cbucket = Couchbase.connect(host=server,port=port,bucket=bucket)
    return cbucket

def save_in_db(cbucket,document):
#    data_md5 = hashlib.md5(json.dumps(document, sort_keys=True)).hexdigest()
#    cbucket.set(data_md5,document)
    cbucket.set(document['fbid'],document)
    return document['fbid']

def saveTextInFile(text,filename):
    result_file = open("/home/user/Downloads/files/%s"%filename,"w")
    result_file.write(str(text.encode('utf-8')) )
    result_file.close()
    return True




access_token = ""
graph = GraphAPI(access_token)

fb_pages = {}


print "starting"
for fb_page in fb_pages:
    feed = graph.get('/'+fb_page+'?fields=feed.limit(30).fields(message,from,created_time,comments.filter(toplevel).fields(message,parent,from,id,created_time),object_id,full_picture),name&locale="en_US"')

    page_name = feed['name']

    feed = feed['feed']['data']
    cb_bucket = connectToDb()

    #print(feed)

    for message in feed:


        try:
            doc_to_store=parse_post(page_name,message)
            data_md5=save_in_db(cb_bucket,doc_to_store)
            saveTextInFile(doc_to_store['text_no_url'],data_md5)
            if "comments" in message:
                comments = message['comments']['data']
                for comment in comments:
                    doc_to_store = parse_comment(page_name,comment)
                    data_md5=save_in_db(cb_bucket,doc_to_store)
                    saveTextInFile(doc_to_store['text_no_url'],data_md5)

        except KeyError,e:
            print str(e)
            continue


