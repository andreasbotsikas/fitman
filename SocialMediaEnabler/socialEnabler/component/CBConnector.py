__author__ = 'mpetyx'

from couchbase import Couchbase


class connector:

    def __init__(self):

        server = "83.212.114.237"
        port = 8091
        # admin_username = "Administrator"
        # admin_password = "dev123456"
        bucket = "default"

        self.cbucket = Couchbase.connect(host=server,port=port,bucket=bucket)