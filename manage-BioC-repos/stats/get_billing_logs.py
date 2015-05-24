#! /usr/bin/env python

import os
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from boto.s3.connection import S3Connection

from boto.s3.bucket import Bucket
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('aws.cfg')

access_key = config.get('aws_credentials', 'access_key')
secret_key = config.get('aws_credentials', 'secret_key')

conn = S3Connection(access_key, secret_key)

b = conn.get_bucket("bioc-aws-billing")

for key in b.list():
    name = key.name.encode('utf-8')

    destdir = "billing-logs"
    if not os.path.exists(destdir):
        #print("Creating directory %s." % destdir)
        os.mkdir(destdir)
    destfile = "%s/%s" % (destdir, name)
    if not os.path.exists(destfile):
        key.get_contents_to_filename("%s/%s" % (destdir, name))

