__author__ = 'mpetyx'

import os
import errno
import json
import time
import urllib2

from CBConnector import connector


def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured


def update(key, value):
    cb = connector().cbucket

    key = key.replace('"', '')
    value = value.replace('"', '')
    try:
        document = cb.get(key)

        document.value["senti_tag"] = value

        cb.set(document.key, document.value)
        print "done for: " + str(key) + "\n"
    except:
        print "oups"
    return True

# parse file
def parse(data):
    file_name = data['"metadata_file"']
    result = data['"prediction(att2)"']

    if update(file_name, result):
        silentremove("./files/"+file_name)

# "label":"unlabeled","metadata_file":"6.txt","metadata_path":"/home/user/Downloads/rapidst/
# SentiTrainData/unlabeledTweets/6.txt","metadata_date":"7/10/2013 5:20 ","confidence(positive)":0.7437240118385439,"confidence(negative)":0.25627598816145614,"prediction(att2)":"positive"

# file_name = "./results/UseLearntModel.json"
#
# json_file = open(file_name,"r")
#
# data = json.load(json_file)
#


# response = urllib2.urlopen('http://83.212.114.237:8081/RA/public_process/readUpdates')
# data = json.load(response)
# # print data
#
# for result in data:
#     parse(result)

t0 = time.time()
while True:
    t1 = time.time()
    if (t1 - t0) >= 1500.0:
        response = urllib2.urlopen('http://83.212.114.237:8081/RA/public_process/readUpdates')
        data = json.load(response)
        # print data

        for result in data:
            parse(result)
        t0 = t1