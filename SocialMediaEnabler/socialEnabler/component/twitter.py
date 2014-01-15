'''
Created on Jan 15, 2014

@author: Evmorfia
'''
import tweepy
import json
import hashlib
import re
import sys
import csv
import time
import datetime
from couchbase import Couchbase
from tweepy.utils import import_simplejson

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
username_re = re.compile(r"(?:^|\s)(@\w+)")

def replace_url(text):
    withoutURL = url_re.sub('_URL',text)
    return withoutURL

def replace_username(text):
    withoutUsername = username_re.sub(' _USERNAME',text)
    return withoutUsername

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

def fix_json(json_tweet,text_no_url):
    fields_wanted = {"created_at","text","lang","retweet_count","id","retweeted","entities"}
    json_to_keep={}
    for k in fields_wanted:
        if json_tweet[k]:
            json_to_keep[k]=json_tweet[k]
    text_no_url = replace_username(text_no_url)
    json_to_keep["text_no_url"]=text_no_url
    user_name = json_tweet["user"]["name"]
    user_name = 'twitter:' + user_name
    json_to_keep["user_name"]= user_name
    user_screen_name = json_tweet["user"]["screen_name"]
    user_screen_name = 'twitter:'+user_screen_name
    json_to_keep["user_screen_name"]=user_screen_name
    json_to_keep["senti_tag"] = "neutral"
    return json_to_keep

def is_swearing(text):
    swear=False
    for w in swear_words:
        if w in text:
            swear=True
            break
    return swear

def fix_text_format(text):
    text_no_url = replace_url(text)
    text_no_url = text_no_url.lower()
    text_no_url = replace_multichars(text_no_url)
    text_no_url = text_no_url.replace('#','')
    return text_no_url

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

swear_words=["ahole","anus","ash0le","ash0les","asholes","ass","assmonkey","assface","assh0le","assh0lez","asshole","assholes","assholz","asswipe","azzhole","bassterds","bastard","bastards","bastardz","basterds","basterdz","biatch","bitch","bitches","blowjob","boffing","butthole","buttwipe","c0ck","c0cks","c0k","carpetmuncher","cawk","cawks","clit","cnts","cntz","cock","cockhead","cock-head","cocks","cocksucker","cock-sucker","crap","cum","cunt","cunts","cuntz","dick","dild0","dild0s","dildo","dildos","dilld0","dilld0s","dominatricks","dominatrics","dominatrix","dyke","enema","fag","fag1t","faget","fagg1t","faggit","faggot","fagit","fags","fagz","faig","faigs","fart","flippingthebird","fudgepacker","fukah","Fuken","fuker","fukk","g00k","gayboy","gaygirl","god-damned","h00r","h0ar","h0re","hells","hoar","hoor","hoore","jackoff","jap","japs","jerk-off","jisim","jiss","jizm","jizz","knob","knobs","knobz","kunt","kunts","kuntz","lipshits","lipshitz","massterbait","masstrbait","masstrbate","masterbaiter","masterbate","masterbates","mothafucker","mothafuker","mothafukkah","mothafukker","motherfucker","motherfukah","motherfuker","motherfukkah","motherfukker","mother-fucker","muthafucker","muthafukah","muthafuker","muthafukkah","muthafukker","n1gr","nastt","nigger;","nigur;","niiger;","niigr;","orafis","orgasim;","orgasm","orgasum","oriface","orifice","orifiss","packi","packie","packy","paki","pakie","paky","pecker","peeenus","peeenusss","peenus","peinus","pen1s","penas","penis","penis-breath","penus","penuus","phuc","phuck","phuk","phuker","phukker","polac","polack","polak","poonani","pr1c","pr1ck","pr1k","pusse","pussee","pussy","puuke","puuker","queer","queers","queerz","qweers","qweerz","qweir","recktum","rectum","retard","sadist","scank","schlong","screwing","semen","shyt","shyte","shytty","shyty","skanck","skank","skankee","skankey","skanks","skanky","slut","sluts","slutty","slutz","son-of-a-bitch","tit","turd","va1jina","vag1na","vagiina","vagina","vaj1na","vajina","vullva","vulva","w0p","wh00r","wh0re","whore","xrated","b!+ch","bitch","blowjob","clit","arschloch","shit","ass","asshole","b!tch","b17ch","b1tch","bastard","bi+ch","boiolas","buceta","c0ck","cawk","chink","cipa","clits","cock","cum","cunt","dildo","dirsa","ejakulate","fatass","fux0r","hoer","hore","jism","kawk","l3itch","l3i+ch","masturbate","masterbat*","masterbat3","motherfucker","s.o.b.","mofo","nazi","nigga","nigger","nutsack","phuck","pimpis","pusse","pussy","scrotum","slut","smut","teets","tits","boobs","b00bs","teez","testical","testicle","titt","w00se","jackoff","wank","whoar","whore","*damn","*dyke","@$$","amcik","andskota","arse*","assrammer","ayir","bi7ch","bitch*","bollock*","breasts","butt-pirate","cabron","cazzo","chraa","chuj","Cock*","cunt*","d4mn","daygo","dego","dick*","dike*","dupa","dziwka","ejackulate","ekrem*","ekto","enculer","faen","fag*","fanculo","feces","feg","felcher","ficken","fitt*","fotze","futkretzn","gay","gook","guiena","h0r","h4x0r","hell","helvete","hoer*","honkey","huevon","hui","injun","jizz","kanker*","kike","klootzak","kraut","knulle","kuk","kuksuger","Kurac","kurwa","kusi*","kyrpa*","lesbo","mamhoon","masturbat*","merd*","mibun","monkleigh","mouliewop","muie","mulkku","muschi","nazis","nepesaurio","nigger*","orospu","paska*","perse","picka","pierdol*","pillu*","pimmel","piss*","pizda","poontsee","poop","porn","p0rn","pr0n","pula","pule","puta","puto","qahbeh","queef*","rautenberg","schaffer","scheiss*","schlampe","schmuck","screw","sharmuta","sharmute","shipal","shiz","skribz","skurwysyn","sphencter","spic","spierdalaj","splooge","suka","b00b*","testicle*","titt*","twat","vittu","wank*","wetback*","wichser","wop*","yed","zabourah","porn"]

#Define filter terms
#filterTerms = [ "ikea","infurma", "othabitat", "koointernationa", "designmilk","light fixture","recycle silk chair","suryasocial", "Furniture_Spain", "@aidima","aidima","mueble","#mueble","@collection"]



json = import_simplejson()

cbucket = Couchbase.connect(host=server,port=port,bucket=bucket)
auth1 = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth1.set_access_token(access_token_key, access_token_secret)

class StreamListener(tweepy.StreamListener):
    json = import_simplejson()
    def on_status(self, tweet):
        #print 'Ran on_status'
        pass
    def on_timeout(self):
        with open("twitterLog.txt", "a") as myfile:
            myfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            myfile.write("***timeout:sleeping for a minute***"+"\n")
        time.sleep(60)
        return True #don't kill the stream
    def on_error(self, status_code):
        with open("twitterLog.txt", "a") as myfile:
            myfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            myfile.write("-----error----"+status_code+"\n")
        return True #don't kill the stream
    def on_data(self, data):
        if data[0].isdigit():
            pass
        else:
            #print 'Ran on_data'
            data_md5 = hashlib.md5(json.dumps(data, sort_keys=True)).hexdigest()
            json_tweet=json.loads(data)
            
            try:
                text = json_tweet["text"]
                text_no_url = fix_text_format(text)
                
                if json_tweet["lang"]:
                    language = json_tweet["lang"]
                    if language == 'en':
                        if is_swearing(text_no_url)==False:
                            json_to_keep = fix_json(json_tweet,text_no_url)
                            cbucket.set(data_md5,json_to_keep)    
                            result_file = open("./files/%s"%data_md5,"w")
                            result_file.write(str(text_no_url.encode('utf-8')) )
                            result_file.close()
                    elif language == 'es':
                        json_to_keep = fix_json(json_tweet,text_no_url)
                        cbucket.set(data_md5,json_to_keep)    
                        result_file = open("./files_spanish/%s"%data_md5,"w")
                        result_file.write(str(text_no_url.encode('utf-8')) )
                        result_file.close()       
                            
                else:
                    json_to_keep = fix_json(json_tweet)
                    cbucket.set(data_md5,json_to_keep)
                
                

                    
            except:
                #e = sys.exc_info()[0]
                #print e
                pass

with open("/home/user/Downloads/AidimaKeywordsTwitter.csv",'rb') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',')
    filterTerms = csv_reader.next()
# print filterTerms
#print filterTerms
l = StreamListener()
streamer = tweepy.Stream(auth=auth1, listener=l, timeout=3000)
streamer.filter(track = filterTerms)