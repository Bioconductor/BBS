#!/usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Jan 17, 2008
###
### email module
###

import sys
import os
import smtplib
import yaml

# On Linux, it seems that from_addr0 must point to the current user or
# nothing is sent (and no error is raised neither)
try:
    from_addr0 = os.environ['USER']
except KeyError:
    from_addr0 = os.environ['USERNAME']

mode = "dry-run" # the default!
redirect_to_addr = None

smtp_host = 'mx.fhcrc.org'
user_agent = 'Thunderbird 2.0.0.6 (Macintosh/20070728)'
errors_to = 'devteam-bioc@fhcrc.org'

# Test this with:
#   import bbs.email
#   from_addr = 'turlututu'
#   to_addrs = ['hpages@fhcrc.org', 'herve.pages@laposte.net']
#   subject = 'test2'
#   msg = 'OOOH'
#   bbs.email.sendtextmail(from_addr, to_addrs, subject, msg)
#   bbs.email.mode = "do-it"
#   bbs.email.sendtextmail(from_addr, to_addrs, subject, msg)
def sendtextmail(from_addr, to_addrs, subject, msg):
    if redirect_to_addr != None:
        to_addrs = [redirect_to_addr]
    to = ', '.join(to_addrs)
    print "BBS>   About to send email to '%s'..." % to,
    msg = 'From: %s\nTo: %s\nSubject: %s\nUser-Agent: %s\nMIME-Version: 1.0\nSender: %s\nErrors-To: %s\n\n%s' % (from_addr, to, subject, user_agent, from_addr, errors_to, msg)
    with open("email_config.yaml", 'r') as stream:
      config = yaml.load(stream)

    server = smtplib.SMTP(config['hostname'], config['port'])
    server.ehlo()
    if config['use_tls']:
      server.starttls()
      server.ehlo()

    if 'username' in config and 'password' in config:
      server.login(config['username'], config['password'])


    #server.set_debuglevel(1)
    if mode == "do-it":
        print "(NOW SENDING!)",
        sys.stdout.flush()
        server.sendmail(from_addr, to_addrs, msg)
    server.quit()
    print "DONE"
    return

# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/67083
def createhtmlmail(html, text, from_addr, to_addrs, subject):
	"""Create a mime-message that will render HTML in popular
	   MUAs, text in better ones"""
	import MimeWriter
	import mimetools
	import cStringIO
	
	out = cStringIO.StringIO() # output buffer for our message 
	htmlin = cStringIO.StringIO(html)
	txtin = cStringIO.StringIO(text)
	
	writer = MimeWriter.MimeWriter(out)
	
	writer.addheader("From", from_addr)
	writer.addheader("To", ', '.join(to_addrs))
	
	#
	# set up some basic headers... we put subject here
	# because smtplib.sendmail expects it to be in the
	# message body
	#
	writer.addheader("Subject", subject)
	writer.addheader("MIME-Version", "1.0")
	#
	# start the multipart section of the message
	# multipart/alternative seems to work better
	# on some MUAs than multipart/mixed
	#
	writer.startmultipartbody("alternative")
	writer.flushheaders()
	#
	# the plain text section
	#
	subpart = writer.nextpart()
	subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
	pout = subpart.startbody("text/plain", [("charset", 'us-ascii')])
	mimetools.encode(txtin, pout, 'quoted-printable')
	txtin.close()
	#
	# start the html subpart of the message
	#
	subpart = writer.nextpart()
	subpart.addheader("Content-Transfer-Encoding", "quoted-printable")
	#
	# returns us a file-ish object we can write to
	#
	pout = subpart.startbody("text/html", [("charset", 'us-ascii')])
	mimetools.encode(htmlin, pout, 'quoted-printable')
	htmlin.close()
	#
	# Now that we're done, close our writer and
	# return the message body
	#
	writer.lastpart()
	msg = out.getvalue()
	out.close()
	#print msg
	return msg

# Test this with:
#   from_addr='turlututu'
#   to_addrs=['hpages@fhcrc.org', 'herve.pages@laposte.net']
#   subject='test3'
#   html_msg='<HTML><BODY style="background: #49A"><H1>OOOH</H1></BODY></HTML>'
#   text_msg='OOOH'
#   import bbs.email
#   bbs.email.sendhtmlmail(from_addr, to_addrs, subject, html_msg, text_msg)
def sendhtmlmail(from_addr, to_addrs, subject, html_msg, text_msg):
    msg = createhtmlmail(html_msg, text_msg, from_addr, to_addrs, subject)
    server = smtplib.SMTP(smtp_host)
    #server.set_debuglevel(1)
    server.sendmail(from_addr0, to_addrs, msg)
    server.quit()
    return


