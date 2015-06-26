#! /usr/bin/env python
#

import datetime
import sys
import sqlite3
import re
import gzip
import bz2

import stats_config
import stats_utils

known_bots = [
    'Yahoo! Slurp',
    'Googlebot',
    'MMAudVid',
    'Gigabot',
    'msnbot',
    'MSNBOT',
    'MSRBOT',
    'NextGenSearchBot',
    'MJ12bot',
    'ia_archiver',
    'Sensis Web Crawler',
    'FAST Enterprise Crawler',
    'yacybot',
    'W3CRobot',
    'MLBot',
    'Gaisbot',
    'noxtrumbot',
    'ljt_ignoreme'
]

unquoted_field_regex = '[^ ]*'
squid_ips_field_regex = '%s(, %s)*' % (unquoted_field_regex, unquoted_field_regex)
apache_time_field_regex = '\[([^]]*)\]'
quoted_field_regex = '"((\\\\"|[^"])*)"'
squid_request_field_regex = '"([^"]+ ([^ ])+ [^ ]+)"'
blank = '\\b|\\S+'
leftover = '.*'

s3_date_field_regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
s3_time_field_regex = '[0-9]{2}:[0-9]{2}:[0-9]{2}' # Note this time is in GMT, unlike 
                                                   # squid and apache times
s3_unquoted_field = '\S+'

apache_fields = (
    squid_ips_field_regex,      # ips
    unquoted_field_regex,       # (ignored)
    unquoted_field_regex,       # (ignored)
    apache_time_field_regex,    # day_month_year/time/utc_offset
    quoted_field_regex,         # request (method/url/protocol)
    unquoted_field_regex,       # errorcode
    unquoted_field_regex,       # bytes
    quoted_field_regex,         # referer
    quoted_field_regex          # user agent
)
APACHELINE_regex = '^(%s) %s %s %s %s (%s) (%s) %s %s$' % apache_fields
APACHELINE_compiled_regex = re.compile(APACHELINE_regex)

squid_fields = (
    squid_ips_field_regex,      # field no 1: ips
    unquoted_field_regex,       # field no 2: (ignored)
    unquoted_field_regex,       # field no 3: (ignored)
    apache_time_field_regex,    # field no 4: day_month_year/time/utc_offset
    #quoted_field_regex,         # field no 5: request (method/url/protocol)
    squid_request_field_regex,  # field no 5: request (method/url/protocol)
    unquoted_field_regex,       # field no 6: errorcode
    unquoted_field_regex,       # field no 7: bytes
    leftover
)
SQUIDLINE_regex = '^(%s) %s %s %s %s (%s) (%s) %s$' % squid_fields
SQUIDLINE_compiled_regex = re.compile(SQUIDLINE_regex)

s3_fields = (
    s3_date_field_regex,    # field no 1: date
    s3_time_field_regex,    # field no 2: time
    s3_unquoted_field,      # field no 3: x-edge-location (ignored)
    s3_unquoted_field,      # field no 4: sc-bytes
    squid_ips_field_regex,  # field no 5: c-ip
    s3_unquoted_field,      # field no 6: method
    s3_unquoted_field,      # field no 7: cs(Host) (ignored)
    s3_unquoted_field,      # field no 8: cs-uri-stem (ignored)
    s3_unquoted_field,      # field no 9: sc-status
    s3_unquoted_field,      # field no 10: cs(Referer)
    s3_unquoted_field,      # field no 11: cs(User-Agent)
    s3_unquoted_field,      # field no 12: cs-uri-query (ignored(?))
    s3_unquoted_field,      # field no 13: cs(Cookie) (ignored)
    s3_unquoted_field,      # field no 14: x-edge-result-type (ignored)
    s3_unquoted_field       # field no 15: x-edge-request-id (ignored)
)

s3_actual_fields = [
'date',
'time',
'x-edge-location',
'sc-bytes',
'c-ip',
'cs-method',
'cs(Host)',
'cs-uri-stem',
'sc-status',
'cs(Referer)',
'cs(User-Agent)',
'cs-uri-query',
'cs(Cookie)',
'x-edge-result-type',
'x-edge-request-id'
]

S3_delim = "#~#~"
#Fields: date time x-edge-location sc-bytes c-ip cs-method cs(Host) cs-uri-stem sc-status cs(Referer) cs(User-Agent) cs-uri-query cs(Cookie) x-edge-result-type x-edge-request-id
#2013-08-28      18:48:44        SEA50   3374    140.107.151.138 GET     d3hzwifbu1gvt4.cloudfront.net   /js/jquery.corner.js    200     http://d3hzwifbu1gvt4.cloudfront.net/   Mozilla/5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_8_4)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/29.0.1547.57%20Safari/537.36 -               Miss    wpmnXHujEa2fSKYppCoGvyUOPOf_3vp0OO-yls1qMmvCI_ZIyvKJaA==
#S3LINE_regex = '^(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)\t(%s)%s$' \
#    % s3_fields
S3LINE_regex = '^(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)#~#~(%s)$' \
    % s3_fields
S3LINE_compiled_regex = re.compile(S3LINE_regex)
S3_compiled_comment_regex = re.compile("^#")

### TODO: Use 'mode' global variable in the parsing functions below to switch
### between Apache format and Squid format.
mode = 0  # 0:Apache, 1:Squid


### ==========================================================================
### All the get_*() functions below will be called with the result of
### SQUIDLINE_compiled_regex.match(logline) (an SRE_Match object) passed
### to their 1st arg, and the input line number passed to their 2nd arg.
### They must extract and return the column value that they are associated
### with (None stands for NULL) or throw a BadInputLine exception describing
### the problem if they can't.
###

class BadInputLine(Exception):
    def __init__(self, desc):
        self.desc = desc
    def __str__(self):
        return self.desc

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### IPS field
###

def get_ips(m, lineno, s3=False, lineobj=None):
    if (s3):
        return(lineobj['c-ip'])
    ## 'm.group(1)' is field no 1 in 'squid_fields'
    val = m.group(1)
    #if stats_utils.strHasBuildNodeIP(val):
    #    raise BadInputLine("BUILDNODE_IN_IPS_FIELD")
    return val

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### TIME field
###

TIME_regex = '^(.*/(.*/.*)):(.*:.*:.*) (.*)$'
TIME_compiled_regex = re.compile(TIME_regex)
TIME_cache = (None, None)  # (TIME_parts, lineno)

def _get_TIME_parts(m, lineno):
    global TIME_cache
    if lineno != TIME_cache[1]:
        ## 'm.group(3)' is field no 4 in 'squid_fields'
        TIME_parts = TIME_compiled_regex.match(m.group(3))
        if TIME_parts == None:
            raise BadInputLine("PARSE_ERROR_IN_TIME_FIELD")
        TIME_cache = (TIME_parts, lineno)
    return TIME_cache[0]

def get_day_month_year(m, lineno, s3, lineobj=None):
    if s3:
        date = lineobj['date']
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        return(dt.strftime("%d/%b/%Y"))
    TIME_parts = _get_TIME_parts(m, lineno)
    return TIME_parts.group(1)

def get_month_year(m, lineno, s3, lineobj=None):
    if s3:
        date = lineobj['date']
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        return(dt.strftime("%b/%Y"))        
    TIME_parts = _get_TIME_parts(m, lineno)
    return TIME_parts.group(2)

def get_time(m, lineno, s3, lineobj=None):
    if s3:
        return lineobj['time']
    TIME_parts = _get_TIME_parts(m, lineno)
    return TIME_parts.group(3)

def get_utc_offset(m, lineno, s3, lineobj=None):
    if s3:
        return("-0000")
    TIME_parts = _get_TIME_parts(m, lineno)
    return TIME_parts.group(4)

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### REQUEST field
###

REQUEST_regex = '^(%s) (.*) (%s)$' % (unquoted_field_regex, unquoted_field_regex)
REQUEST_compiled_regex = re.compile(REQUEST_regex)
REQUEST_cache = (None, None)  # (REQUEST_parts, lineno)

def _get_REQUEST_parts(m, lineno):
    global REQUEST_cache
    if lineno != REQUEST_cache[1]:
        ## 'm.group(4)' is field no 5 in 'squid_fields'
        REQUEST_parts = REQUEST_compiled_regex.match(m.group(4))
        if REQUEST_parts == None:
            raise BadInputLine("PARSE_ERROR_IN_REQUEST_FIELD")
        REQUEST_cache = (REQUEST_parts, lineno)
    return REQUEST_cache[0]

def get_method(m, lineno, s3, lineobj=None):
    if s3:
        method = lineobj['cs-method']
    else:
        REQUEST_parts = _get_REQUEST_parts(m, lineno)
        method = REQUEST_parts.group(1)
    if method == "HEAD":
        raise BadInputLine("INVALID_HTTP_METHOD")
    return method

def get_url(m, lineno, s3, lineobj=None):
    if s3:
        return(lineobj['cs-uri-stem'])
    REQUEST_parts = _get_REQUEST_parts(m, lineno)
    return REQUEST_parts.group(2)

def get_protocol(m, lineno, s3, lineobj=None):
    if s3:
        # fake it:
        return("HTTP/1.1")
    REQUEST_parts = _get_REQUEST_parts(m, lineno)
    return REQUEST_parts.group(3)

### Split the URL subfield
PKGPATH_regex = '/(src/contrib|bin/.*/contrib/[^/]*)/([^/_]*)_([^/_]*)\.(tar\.gz|zip|tgz)$'
SQUID_URL_regex = '.*bioconductor.org(.*)' + PKGPATH_regex
SQUID_URL_compiled_regex = re.compile(SQUID_URL_regex)
APACHE2_URL_regex = '(/.*)' + PKGPATH_regex
APACHE2_URL_compiled_regex = re.compile(APACHE2_URL_regex)
URL_compiled_regex = None
URL_cache = (None, None)  # (URL_parts, lineno)

def _get_URL_parts(m, lineno, s3=False, lineobj=None):
    global URL_cache
    if lineno != URL_cache[1]:
        URL = get_url(m, lineno, s3, lineobj)
        if URL_compiled_regex == None:
            print 'URL_compiled_regex must be set to SQUID_URL_compiled_regex or APACHE2_URL_compiled_regex'
            sys.exit("==> EXIT")
        URL_parts = URL_compiled_regex.match(URL)
        if URL_parts == None:
            raise BadInputLine("NOT_PKG_DOWNLOAD_IN_URL_PART_OF_REQUEST_FIELD")
        URL_cache = (URL_parts, lineno)
    return URL_cache[0]

def get_biocrepo_relurl(m, lineno, s3, lineobj=None):
    URL_parts = _get_URL_parts(m, lineno, s3, lineobj)
    return URL_parts.group(1)

def getBiocRepo(relurl):
    relurl = relurl.lower()
    if relurl == '/cran':
        return None
    biocrepos = ['annotation', 'experiment', 'extra', 'omegahat', 'monograph', 'lindsey']
    for biocrepo in biocrepos:
        if relurl.find(biocrepo) != -1:
            return biocrepo
    return 'bioc'

def get_biocrepo(m, lineno, s3, lineobj=None):
    relurl = get_biocrepo_relurl(m, lineno, s3)
    val = getBiocRepo(relurl)
    if val == None:
        raise BadInputLine("NOT_BIOC_REPO_IN_URL_PART_OF_REQUEST_FIELD")
    return val

def get_biocversion(m, lineno, s3, lineobj=None):
    return None  # FIXME

def get_package(m, lineno, s3, lineobj=None):
    URL_parts = _get_URL_parts(m, lineno, s3)
    return URL_parts.group(3)

def get_pkgversion(m, lineno, s3, lineobj=None):
    URL_parts = _get_URL_parts(m, lineno, s3, lineobj)
    return URL_parts.group(4)

def get_pkgtype(m, lineno, s3, lineobj=None):
    URL_parts = _get_URL_parts(m, lineno, s3)
    return URL_parts.group(5)

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### ERRORCODE field
###

def get_errorcode(m, lineno, s3, lineobj):
    if (s3):
        val = lineobj['sc-status']
    else:
        val = m.group(6)
    ## 'm.group(6)' is field no 6 in 'squid_fields'
    #if val[0] != '2':
    ## NB: CloudFront may legitimately use codes other than 200?
    if val != '200':
        raise BadInputLine("NOT200_IN_ERRORCODE_FIELD")
    return val

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### BYTES field
###

def get_bytes(m, lineno, s3, lineobj=None):
    if s3:
        val = int(lineobj['sc-bytes'])
    else:
        val = m.group(7)
    ## 'm.group(7)' is field no 7 in 'squid_fields'
    if val == '-':
        val = None
    else:
        val = int(val)
    return val

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### REFERER field
###

# Is in the Apache logs but not in the Squid logs
def get_referer(m, lineno, s3, lineobj=None):
    #return m.group(8)
    return None

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### USERAGENT field
###

bots_regex = ''
for bot in known_bots:
    if bots_regex != '':
        bots_regex = bots_regex + '|'
    bots_regex = bots_regex + bot
bots_regex = '(%s)' % bots_regex

bots_compiled_regex = re.compile(bots_regex)

# Is in the Apache logs but not in the Squid logs
def get_user_agent(m, lineno, s3, lineobj=None):
    #val = m.group(10)
    #if bots_compiled_regex.match(val):
    #    raise BadInputLine("BOT_IN_USERAGENT_FIELD")
    return None

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
### Dictionary of SQL col definitions and their associated get_*() function
###

access_log_col2getter = {
  'ips': get_ips,
  'day_month_year': get_day_month_year,
  'month_year': get_month_year,
  'time': get_time,
  'utc_offset': get_utc_offset,
  'method': get_method,
  'url': get_url,
  'protocol': get_protocol,
  'errorcode': get_errorcode,
  'bytes': get_bytes,
  'referer': get_referer,
  'user_agent': get_user_agent,
  'biocrepo_relurl': get_biocrepo_relurl,
  'biocrepo': get_biocrepo,
  'biocversion': get_biocversion,
  'package': get_package,
  'pkgversion': get_pkgversion,
  'pkgtype': get_pkgtype,
}


### ==========================================================================

# unlike shell processes, a return code of 0 signifies an error
# and 1 signifies no error.
def importLogLine(c, logline, lineno, logfile, s3Fields, s3=False):
    lineobj = None
    if s3:
        #if (logline[0] == '#'):
        if re.match(S3_compiled_comment_regex, logline):
            return 0 # skip comments silently
        segs = logline.rstrip().split("\t")
        lineobj = {}
        i = 0
        newline = ""
        for key in s3Fields:
            lineobj[key] = segs[i]
            if key == "cs(Cookie)":
                lineobj[key] = "-"
            newline += lineobj[key] + S3_delim
            i += 1
        newline = re.sub(S3_delim + '$', "", newline)
        #m = S3LINE_compiled_regex.match(newline) # too slow!
        m = None
        if not len(segs) == len(s3Fields):
            print 'make_db.py: failed to parse S3 line %d (file %s),' % (lineno, logfile),
            print 'rejecting it. See line below:'
            print newline
            return 0
        colnames = access_log_col2getter.keys()
    else:
        mm = re.search('"Amazon CloudFront"$', logline.rstrip())
        if (mm is not None):
            return 0
        m = SQUIDLINE_compiled_regex.match(logline)
        if not m:
            print 'make_db.py: failed to parse line %d (file %s),' % (lineno, logfile),
            print 'rejecting it. See line below:'
            print logline
            #sys.exit("==> EXIT")
            return 0
        colnames = access_log_col2getter.keys() # NB. not sorted?
    col2val = {}
    try:
        for colname in colnames:
            col2val[colname] = access_log_col2getter[colname](m, lineno,
                s3, lineobj)
    except BadInputLine:
        return 0
    try:
        stats_utils.SQL_insertRow(c, 'access_log', col2val)
    except sqlite3.Error, error:
        print 'INSERT failed for line %d (file %s)' % (lineno, logfile)
        raise
    return 1

def getS3Fields(logfile):
    if logfile[-2:] == 'gz':
        file = gzip.open(logfile, 'r')
    elif logfile[-3:] == 'bz2':
        file = bz2.BZ2File(logfile)
    else:
        file = open(logfile, 'r')
    i = -1
    field_line = None
    for line in file:
        i += 1
        if i == 0:
            continue
        if i == 1:
            field_line = line
            break
    file.close()
    if field_line is None:
        return None
    return(field_line.strip().replace("#Fields: ", "").split(" "))


def importLogFiles(c, logfiles, trash_file, s3=False):
    total_imported_lines = total_rejected_lines = 0
    for logfile in logfiles:
        if logfile[-2:] == 'gz':
            file = gzip.open(logfile, 'r')
        elif logfile[-3:] == 'bz2':
            file = bz2.BZ2File(logfile)
        else:
            file = open(logfile, 'r')
        print 'Importing log file %s ...' % logfile,
        nb_imported_lines = nb_rejected_lines = 0
        lineno = 0
        if s3:
            s3Fields = getS3Fields(logfile)
            if s3Fields is None:
                print "File %s has no #Fields line, skipping." % logfile
                continue
        else:
            s3Fields = None
        for line in file:
            lineno = lineno + 1
            ret = importLogLine(c, line, lineno, logfile, s3Fields, s3=s3,)
            if ret == 0:
                nb_rejected_lines += 1
                trash_file.write('%s' % line)
            else:
                nb_imported_lines += 1
        print 'OK'
        print '  %d imported lines / %d rejected lines' % (nb_imported_lines, nb_rejected_lines)
        file.close()
        total_imported_lines += nb_imported_lines
        total_rejected_lines += nb_rejected_lines
    return (total_imported_lines, total_rejected_lines)

conn = stats_utils.SQL_createDB(stats_config.dbfile)
c = conn.cursor()
stats_utils.SQL_createAccessLogTable(c)

#trash_file = open('trash.log', 'w')
trash_file = open('/dev/null', 'w')  # trash_file is really too big these days!
total_imported_lines = total_rejected_lines = 0

# Set 'from_date' to None to process all log files (takes a very long time!)
from_date = datetime.date(2014, 1, 1)

print ''
print 'START importing Squid logs.'
URL_compiled_regex = SQUID_URL_compiled_regex
logfiles = stats_utils.getSquidAccessLogFiles(from_date)
total = importLogFiles(c, logfiles, trash_file, s3=False)
print 'END importing Squid logs.'
print '  %d imported Squid lines / %d rejected Squid lines' % (total[0], total[1])
total_imported_lines += total[0]
total_rejected_lines += total[1]

print ''
print 'START importing Apache2 logs.'
URL_compiled_regex = APACHE2_URL_compiled_regex
logfiles = stats_utils.getApache2AccessLogFiles(from_date)
total = importLogFiles(c, logfiles, trash_file, s3=False)
print 'END importing Apache2 logs.'
print '  %d imported Apache2 lines / %d rejected Apache2 lines' % (total[0], total[1])
total_imported_lines += total[0]
total_rejected_lines += total[1]

print ''
print 'START importing S3 logs.'
URL_compiled_regex = APACHE2_URL_compiled_regex # ok?
logfiles = stats_utils.getCloudFrontAccessLogFiles(from_date)
total = importLogFiles(c, logfiles, trash_file, s3=True)
print 'END importing S3 logs.'
print '  %d imported S3 lines / %d rejected S3 lines' % (total[0], total[1])
total_imported_lines += total[0]
total_rejected_lines += total[1]

trash_file.close()

conn.commit()
print 'Creating index on access_log.ips column ...'
c.execute('CREATE INDEX ipsI ON access_log (ips)')
print 'Creating index on access_log.month_year column ...'
c.execute('CREATE INDEX month_yearI ON access_log (month_year)')
print 'Creating index on access_log.package column ...'
c.execute('CREATE INDEX packageI ON access_log (package)')
conn.commit()

c.close()
conn.close()

print ''
print '%d lines were imported in total' % total_imported_lines
print '%d lines were rejected in total' % total_rejected_lines

