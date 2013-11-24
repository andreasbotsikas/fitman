__author__ = 'mpetyx'


import csv
from couchbase import Couchbase

#Define Database connection creds
# server = "localhost"
server = "83.212.114.237"
port = 8091
# admin_username = "Administrator"
# admin_password = "dev123456"
bucket = "default"

data = []

cbucket = Couchbase.connect(host=server,port=port,bucket=bucket)
result = cbucket.query("document%2Ftext","text_only", limit=1000)
# http://83.212.114.237:8092/default/_design/document%2Ftext/_view/text_only

out = csv.writer(open("myfile.csv","w"), delimiter=',',quoting=csv.QUOTE_ALL)

for row in result:
    # data.append( str(row.value.encode('utf-8') ))
    data = [ str(row.value.encode('utf-8')), " \n"]
    out.writerow(data)