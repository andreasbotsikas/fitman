__author__ = 'mpetyx'

from couchbase import Couchbase

#Define Database connection creds
# server = "localhost"
server = "83.212.114.237"
port = 8091
admin_username = "Administrator"
admin_password = "dev123456"
bucket = "default"

data = []

cb = Couchbase.connect(host=server,port=port,bucket=bucket)


def update(key, value):

    document = cb.get(key)

    document["senti_tag"] = value

    cb.set(key, document)
    return 1


def multiple_values_update( lista ):

    for item in lista:

        update(item['key'], item['value'])

    cb._close()