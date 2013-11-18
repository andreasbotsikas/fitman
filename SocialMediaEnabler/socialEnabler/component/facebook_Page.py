__author__ = 'mpetyx'

from facepy import GraphAPI
from pprint import pprint
access_token = "CAACEdEose0cBANiiJrpe30QCgJbtDSayhdZCbWYQEZBHNJvhvJ5wsNYMjNU3ZAVd1bQ2dRICE7ienZCjr0wqMKg7eS3cnmCKv3rL2jwJ1oOZBsKVuWd9zIvbdmvP0B2Cl1CdTEqq4IVNtZBA1zmRwQvqJZBHZBRaV3ZBfHuCWeWpgWGWZBFU41VU302CmggFRYYO0ZD"
graph = GraphAPI(access_token)

feed = graph.get('/coca-cola?fields=feed.limit(50).fields(message,comments)')

feed = feed['feed']['data']

# pprint(feed)

for message in feed:

    try:
        pprint(str(message['message'].encode('utf-8')))
    except KeyError,e :
        continue