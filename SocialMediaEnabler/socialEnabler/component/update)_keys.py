__author__ = 'mpetyx'

import os, errno, json

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError as e: # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occured

def update(key, value):

    cb = None

    document = cb.get(key)

    document["senti_tag"] = value

    cb.set(key, document)
    return 1

# parse file
def parse(data):

    file_name = data["metadata_file"]
    result = data["prediction(att2)"]

    if update(file_name,result):
        silentremove(file_name)

# "label":"unlabeled","metadata_file":"6.txt","metadata_path":"/home/user/Downloads/rapidst/
# SentiTrainData/unlabeledTweets/6.txt","metadata_date":"7/10/2013 5:20 ","confidence(positive)":0.7437240118385439,"confidence(negative)":0.25627598816145614,"prediction(att2)":"positive"

file_name = "./results/UseLearntModel.json"

json_file = open(file_name,"r")

data = json.load(json_file)

for result in data:
    print result["metadata_file"]
    print result["prediction(att2)"]

# print len(data)
#
# print data[1]
# print data[1]["metadata_file"]
# print data[1]["prediction(att2)"]