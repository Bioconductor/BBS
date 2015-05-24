#! /usr/bin/env python

from time import localtime, strftime
import os
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from boto.s3.connection import S3Connection

from boto.s3.bucket import Bucket
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('aws.cfg')

start = strftime("%Y-%m-%d %H:%M:%S", localtime())
print("get_s3_logs.py starting at %s" % start)




access_key = config.get('aws_credentials', 'access_key')
secret_key = config.get('aws_credentials', 'secret_key')

conn = S3Connection(access_key, secret_key)

print("Getting bucket object....")
b = conn.get_bucket("bioc-cloudfront-logs")

downloadcount = 0

print("Iterating through bucket list...")
for key in b.list():
    name = key.name.encode('utf-8')
    segs = name.split(".")
    segs2 = segs[1].split("-")
    segs2.pop()
    date = "-".join(segs2)

    destdir = "bioc-access-logs/s3/%s" % date
    if not os.path.exists(destdir):
        print("Creating directory %s." % destdir)
        os.mkdir(destdir)
    destfile = "%s/%s" % (destdir, name)
    if not os.path.exists(destfile):
        key.get_contents_to_filename("%s/%s" % (destdir, name))
        if (downloadcount > 0 and downloadcount % 50 == 0):
            print "Count of downloaded log files: %s" % downloadcount
        downloadcount += 1

print("Total files downloaded: %s." % downloadcount)
end = strftime("%Y-%m-%d %H:%M:%S", localtime())
print("get_s3_logs.py end at %s" % end)
