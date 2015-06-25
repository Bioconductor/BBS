import sys
import os
import string
import sqlite3
import re
import time
import math
import matplotlib
matplotlib.use('agg')
import pylab
### urllib.urlopen() doesn't raise an error when the object is not found (HTTP
### Error 404) but urllib2.urlopen() does (raises an urllib2.HTTPError object)
import urllib2

import stats_config

#access_logfiles_regex = '^access.log-2008(07|08|09|10).*\.gz$'
#access_logfiles_regex = '^access.log-200[78].*\.gz$'
#access_logfiles_regex = '^(access(-bioc)?.log-20(08|09|10|11|12).*\.gz|bioconductor-access.log-.*)$'
access_logfiles_regex = '^(access(-bioc)?.log-20(08|09|10|11|12).*\.gz|bioconductor-access.log.*)$'

### Follows symlinks (if they are supported).
def getMatchingFiles(dir=".", regex="", full_names=False, recurse=False,
    match_type="match"):
    p = re.compile(regex)
    matching_files = []
    dir_files = []
    ## Note:: with current behavior, if recurse, then code
    ## behaves as though full_names=True, regardless of how it's set.
    if recurse:
        for dirname, dirnames, filenames in os.walk('bioc-access-logs/s3'):
            for filename in filenames:
                dir_files.append(os.path.join(dirname, filename))
    else:
        dir_files = os.listdir(dir)
    for file in dir_files:
        if match_type == "match":
            m = p.match(file)
        else:
            m = p.search(file)
        if not m:
            continue
        if recurse:
            full_name = file
        else:
            full_name = os.path.join(dir, file)
        if not os.path.isfile(full_name):
            continue
        if full_names:
            matching_files.append(full_name)
        else:
            matching_files.append(file)
    return matching_files

def getSquidAccessLogFiles():
    files = []
    for dir in stats_config.squid_access_logdirs:
        files.extend(getMatchingFiles(dir, access_logfiles_regex, True))
    files.sort(lambda x, y: cmp(string.lower(x), string.lower(y)))
    return files

def getApache2AccessLogFiles():
    files = []
    for dir in stats_config.apache2_access_logdirs:
        files.extend(getMatchingFiles(dir, access_logfiles_regex, True))
    files.sort(lambda x, y: cmp(string.lower(x), string.lower(y)))
    return files


def getS3AccessLogFiles():
    files = []
    s3_logfiles_regex = ""
    for dir in stats_config.s3_access_logdirs:
        files.extend(getMatchingFiles(dir, "\.gz$", True, True, "search"))
    files.sort(lambda x, y: cmp(string.lower(x), string.lower(y)))
    return files

def strHasBuildNodeIP(s):
    for ip in stats_config.buildnode_ips:
        if s.find(ip) != -1:
            return True
    return False


### ==========================================================================
### SQL low-level utilities
###

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### DB schema
###

access_log_col2type = {
  'ips': 'TEXT NOT NULL',
  'day_month_year': 'TEXT NOT NULL',
  'month_year': 'TEXT NOT NULL',
  'time': 'TEXT NOT NULL',
  'utc_offset': 'TEXT NOT NULL',
  'method': 'TEXT NOT NULL',
  'url': 'TEXT NOT NULL',
  'protocol': 'TEXT NOT NULL',
  'errorcode': 'TEXT NOT NULL',
  'bytes': 'INTEGER NULL',
  'referer': 'TEXT NULL',
  'user_agent': 'TEXT NULL',
  'biocrepo_relurl': 'TEXT NULL',
  'biocrepo': 'TEXT NULL',
  'biocversion': 'TEXT NULL',
  'package': 'TEXT NULL',
  'pkgversion': 'TEXT NULL',
  'pkgtype': 'TEXT NULL',
}

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### Making the DB.
###

def SQL_createDB(dbfile):
    if os.path.exists(dbfile):
        print 'Removing existing %s file ...' % dbfile
        os.remove(dbfile)
    return sqlite3.connect(dbfile)

def SQL_createAccessLogTable(c):
    sql = ''
    for colname in access_log_col2type.keys():
        if sql != '':
            sql += ', '
        sql += colname + ' ' + access_log_col2type[colname]
    sql = 'CREATE TABLE access_log (%s)' % sql
    c.execute(sql)
    return

def SQL_insertRow(c, tablename, col2val):
    cols = ','.join(col2val.keys())
    placeholders = []
    for val in col2val.values():
        placeholders.append('?')
    placeholders = ','.join(placeholders)
    sql = 'INSERT INTO %s (%s) VALUES (%s)' % (tablename, cols, placeholders)
    c.execute(sql, tuple(col2val.values()))
    return sql

### - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
### Querying the DB.
###

def SQL_connectToDB(dbfile):
    if not os.path.exists(dbfile):
        print '%s file not found. Did you run make_db.sh?' % dbfile
        sys.exit("==> EXIT")
    return sqlite3.connect(dbfile)

def SQL_globalFilter():
    date_is_in_range = "month_year IN ('%s')" % \
                       "','".join(stats_config.lastmonths)
    global_filter = date_is_in_range
    return global_filter

def SQL_getDistinctPackages(c, biocrepo='bioc'):
    sql = "SELECT DISTINCT package FROM access_log WHERE biocrepo='%s' AND %s" \
        % (biocrepo, SQL_globalFilter())
    c.execute(sql)
    pkgs = []
    for row in c:
        pkgs.append(str(row[0]))
    #pkgs.sort(lambda u, v: cmp(string.lower(u), string.lower(v)))
    return pkgs

def SQL_countDownloadsPerMonth(c, sql_where):
    print 'Counting downloads-per-month for "%s" ...' % sql_where,
    sys.stdout.flush()
    sql = "SELECT month_year, count(*) FROM access_log" \
        + " WHERE (%s) AND (%s)" % (SQL_globalFilter(), sql_where) \
        + " GROUP BY month_year"
    c.execute(sql)
    month_to_Y = {}
    for month in stats_config.lastmonths:
        month_to_Y[month] = 0
    for row in c:
        month = row[0]
        if month in month_to_Y.keys():
            month_to_Y[month] = row[1]
    print 'OK'
    return month_to_Y

def SQL_countIPsPerMonth(c, sql_where):
    print 'Counting distinct IPs-per-month for "%s" ...' % sql_where,
    sys.stdout.flush()
    sql = "SELECT month_year, count(DISTINCT ips) FROM access_log" \
        + " WHERE (%s) AND (%s)" % (SQL_globalFilter(), sql_where) \
        + " GROUP BY month_year"
    c.execute(sql)
    month_to_Y = {}
    for month in stats_config.lastmonths:
        month_to_Y[month] = 0
    for row in c:
        month = row[0]
        if month in month_to_Y.keys():
            month_to_Y[month] = row[1]
    print 'OK'
    return month_to_Y

def SQL_countIPs(c, sql_where):
    print 'Counting distinct IPs for "%s" ...' % sql_where,
    sys.stdout.flush()
    sql = "SELECT count(DISTINCT ips) FROM access_log" \
        + " WHERE (%s) AND (%s)" % (SQL_globalFilter(), sql_where)
    c.execute(sql)
    for row in c:
        print 'OK'
        return row[0]

def SQL_countDownloadsPerIP(c, sql_where):
    print 'Counting downloads-per-IP for "%s" ...' % sql_where,
    sys.stdout.flush()
    sql = "SELECT ips, count(*) FROM access_log" \
        + " WHERE (%s) AND (%s)" % (SQL_globalFilter(), sql_where) \
        + " GROUP BY ips"
    c.execute(sql)
    ip_to_Y = {}
    for row in c:
        ip_to_Y[row[0]] = row[1]
    print 'OK'
    return ip_to_Y


### ==========================================================================
### Make HTML report.
###

def write_top_asHTML(out, title, css_file):
    out.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"')
    out.write(' "http://www.w3.org/TR/html4/loose.dtd">\n')
    out.write('<HTML>\n')
    out.write('<HEAD>')
    out.write('<TITLE>%s</TITLE>' % title)
    out.write('<LINK rel="stylesheet" href="%s" type="text/css">' % css_file)
    out.write('</HEAD>\n')
    return

def write_topright_links_asHTML(out, href1, text1, href2, text2):
    out.write('<TABLE style="width: 100%; border-spacing: 0px; ')
    out.write('border-collapse: collapse;"><TR>')
    out.write('<TD style="padding: 0px; text-align: right;">')
    out.write('<I><A href="%s">%s</A></I>' % (href1, text1))
    out.write('</TD>')
    out.write('<TD style="padding: 0px; text-align: right;">')
    out.write('<I><A href="%s">%s</A></I>' % (href2, text2))
    out.write('</TD>')
    out.write('</TR></TABLE>\n')
    return

def write_goback_asHTML(out, href, main_page_title):
    out.write('<TABLE style="width: 100%; border-spacing: 0px; border-collapse: collapse;"><TR>')
    out.write('<TD style="padding: 0px; text-align: left;">')
    out.write('<I><A href="%s">Back to the &quot;%s&quot;</A></I>' % (href, main_page_title))
    out.write('</TD>')
    out.write('</TR></TABLE>\n')
    return

def write_text_in_TABLE(out, motd):
    if motd == "":
        return
    out.write('<TABLE class="motd">')
    out.write('<TR><TD>%s</TD></TR>' % motd)
    out.write('</TABLE>\n')
    return

# 'tm' must be a <type 'time.struct_time'> object as returned by
# time.localtime(). See http://docs.python.org/lib/module-time.html
# for more info.
# Example:
#   >>> dateString(time.localtime())
#   '2007-12-07 10:03:15 -0800 (Fri, 07 Dec 2007)'
# Note that this is how 'svn log' and 'svn info' format the dates.
def dateString(tm):
    if tm.tm_isdst:
        utc_offset = time.altzone # 7 hours in Seattle
    else:
        utc_offset = time.timezone # 8 hours in Seattle
    utc_offset /= 3600
    format = "%%Y-%%m-%%d %%H:%%M:%%S -0%d00 (%%a, %%d %%b %%Y)" % utc_offset
    return time.strftime(format, tm)

def currentDateString():
    return dateString(time.localtime())

def write_timestamp_asHTML(out):
    out.write('<P style="text-align: center;">\n')
    out.write('<I>This page was generated on %s.</I>\n' % currentDateString())
    out.write('</P>\n')
    return

def get_link_to_package_home(pkg, biocversion):
    for biocrepo in ['bioc', 'data/annotation', 'data/experiment', 'extra']:
        url = 'http://bioconductor.org/packages/%s/%s/html/%s.html' % \
              (biocversion, biocrepo, pkg)
        try:
            urllib2.urlopen(url)
        except urllib2.HTTPError:
            continue
        return url
    return None

def write_links_to_package_home(out, pkg):
    url1 = get_link_to_package_home(pkg, "release")
    url2 = get_link_to_package_home(pkg, "devel")
    out.write('<P style="text-align: center;">')
    if url1 == None and url2 == None:
        out.write('Note that <B>%s</B> doesn\'t belong to the ' % pkg)
        out.write('current release or devel version of Bioconductor anymore.')
        out.write('</P>\n')
        return
    out.write('<B>%s</B> home page: ' % pkg)
    if url1 != None:
        out.write('<A HREF="%s">release version</A>' % url1)
    if url2 != None:
        if url1 != None:
            out.write(', ')
        out.write('<A HREF="%s">devel version</A>' % url2)
    out.write('.</P>\n')
    return

def make_barplot2(title, barplot_file, barlabels,
                  barlabel_to_Y1, Y1_label, Y1_color,
                  barlabel_to_Y2, Y2_label, Y2_color, ymax=None):
    Y1_vals = []
    Y2_vals = []
    ymax0 = 0
    for label in barlabels:
        Y1_vals.append(barlabel_to_Y1[label])
        Y2_vals.append(barlabel_to_Y2[label])
        if barlabel_to_Y1[label] > ymax0:
            ymax0 = barlabel_to_Y1[label]
        if barlabel_to_Y2[label] > ymax0:
            ymax0 = barlabel_to_Y2[label]
    pylab.clf()
    ind = pylab.arange(len(Y1_vals))
    width = 0.40  # the width of the bars
    rects1 = pylab.bar(ind,         Y1_vals, width, color=Y1_color)
    rects2 = pylab.bar(ind + width, Y2_vals, width, color=Y2_color)
    pylab.title(title)
    xlabels = []
    for i in range(0, len(barlabels)):
        if i % 3 != 2:
            label = ''
        else:
            label = barlabels[i]
        xlabels.append(label)
    pylab.xticks(ind + width, xlabels)
    if ymax == None:
        ymax = ymax0 * 1.25
    dy = int(10.0 ** (round(math.log(ymax)/math.log(10.0)) - 1.0))
    if dy < 1:
        dy = 1
    if ymax / dy > 10.0:
        dy *= 2
    pylab.yticks(pylab.arange(0, ymax + 1, dy))
    #matplotlib.pyplot.yscale('log')  # doesn't work properly!
    #pylab.grid(True)
    pylab.legend((rects1[0], rects2[0]), (Y1_label, Y2_label), loc=2)
    pylab.savefig(barplot_file, format='png')
    return

def make_barplot2ylog(title, barplot_file, barlabels,
                      barlabel_to_Y1, Y1_label, Y1_color,
                      barlabel_to_Y2, Y2_label, Y2_color, Ymax=None):
    y1_vals = []
    y2_vals = []
    Ymax0 = 0
    for label in barlabels:
        Y1 = barlabel_to_Y1[label]
        if Y1 > Ymax0:
            Ymax0 = Y1
        y1_vals.append(math.log10(1 + Y1))
        Y2 = barlabel_to_Y2[label]
        if Y2 > Ymax0:
            Ymax0 = Y2
        y2_vals.append(math.log10(1 + Y2))
    pylab.clf()
    xtickat = pylab.arange(len(y1_vals)) + 0.5
    width = 0.40  # the width of the bars
    rects1 = pylab.bar(xtickat - width, y1_vals, width, color=Y1_color)
    rects2 = pylab.bar(xtickat,         y2_vals, width, color=Y2_color)
    xlabels = []
    for i in range(0, len(barlabels)):
        if i % 3 != 2:
            label = ''
        else:
            label = barlabels[i]
        xlabels.append(label)
    pylab.xticks(xtickat, xlabels)
    if Ymax == None:
        Ymax = Ymax0
    if Ymax < 100:
        nb_pow10ticks = 3
    else:
        nb_pow10ticks = int(math.log10(Ymax)) + 2
    ytickat = [0]
    ylabels = ['0']
    for i in range(0, nb_pow10ticks):
        at = 10 ** i
        y = math.log10(1 + at)
        ytickat.append(y)
        ylabels.append(str(at))
        if i < nb_pow10ticks - 1:
            pylab.axhline(y, color='black', alpha=0.16)
            for j in range(1, 10):
                y = math.log10(1 + j * at)
                ytickat.append(y)
                if nb_pow10ticks <= 6 and (j == 2 or j == 5):
                    ylabel = str(j *at)
                else:
                    ylabel = ''
                ylabels.append(ylabel)
                pylab.axhline(y, color='black', alpha=0.08)
    pylab.yticks(ytickat, ylabels)
    pylab.title(title)
    pylab.legend((rects1[0], rects2[0]), (Y1_label, Y2_label), loc=8)
    pylab.savefig(barplot_file, format='png')
    return

def write_DownloadsPerMonth_TABLE(c, out, title, sql_where,
                                  barplot_file, ymax=None):
    month_to_Y1 = SQL_countIPsPerMonth(c, sql_where)
    allmonths_Y1 = SQL_countIPs(c, sql_where)
    month_to_Y2 = SQL_countDownloadsPerMonth(c, sql_where)
    Y1_color = '#8888ff'
    Y2_color = '#ddddff'
    Y1_style = 'style="text-align: right; background: %s"' % Y1_color
    Y2_style = 'style="text-align: right; background: %s"' % Y2_color

    make_barplot2ylog(title, barplot_file, stats_config.lastmonths,
                      month_to_Y1, 'Nb of distinct IPs', Y1_color,
                      month_to_Y2, 'Nb of downloads', Y2_color, ymax)
    out.write('<TABLE><TR>\n')
    out.write('<TD>')
    out.write('<IMG SRC="%s" WIDTH="600px" HEIGHT="450px">' % barplot_file)
    out.write('</TD><TD>')
    out.write('<TABLE class="stats">\n')
    out.write('<TR>')
    out.write('<TH style="text-align: right">Month</TH>')
    out.write('<TH %s>Nb&nbsp;of distinct&nbsp;IPs</TH>' % Y1_style)
    out.write('<TH %s>Nb&nbsp;of downloads</TH>' % Y2_style)
    out.write('</TR>\n')
    allmonths_Y2 = 0
    for month in stats_config.lastmonths:
        out.write('<TR>')
        out.write('<TD style="text-align: right">%s</TD>' % month)
        out.write('<TD %s>%d</TD>' % (Y1_style, month_to_Y1[month]))
        out.write('<TD %s>%d</TD>' % (Y2_style, month_to_Y2[month]))
        out.write('</TR>\n')
        allmonths_Y2 += month_to_Y2[month]
    out.write('<TR>')
    out.write('<TH style="text-align: right">All&nbsp;months</TH>')
    out.write('<TH %s>%d</TH>' % (Y1_style, allmonths_Y1))
    out.write('<TH %s>%d</TH>' % (Y2_style, allmonths_Y2))
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    out.write('</TD>')
    out.write('</TR></TABLE>\n')
    return allmonths_Y1

def write_DownloadsPerIP_TABLE(c, out, title, sql_where, maxrows=None):
    ip_to_Y = SQL_countDownloadsPerIP(c, sql_where)
    ips = ip_to_Y.keys()
    ips.sort(lambda u, v: ip_to_Y[v] - ip_to_Y[u])
    out.write('<TABLE>\n')
    out.write('<TR><TH style="text-align: left">IP</TH>')
    out.write('<TH style="text-align: right">Nb&nbsp;of downloads</TH></TR>\n')
    r = total1 = total2 = 0
    for ip in ips:
        r += 1
        if maxrows == None or r <= maxrows:
            try:
                machine_name = stats_config.known_fhcrc_machines[ip]
                ip_html = '%s&nbsp;(%s)' % (ip, machine_name)
            except KeyError:
                ip_html = ip
            out.write('<TR>')
            out.write('<TD>%s</TD>' % ip_html)
            out.write('<TD style="text-align: right">%s</TD>' % ip_to_Y[ip])
            out.write('</TR>\n')
            total1 += ip_to_Y[ip]
        else:
            total2 += ip_to_Y[ip]
    if total2 != 0:
        out.write('<TR style="font-style: italic">')
        out.write('<TD>others</TD>')
        out.write('<TD style="text-align: right">%s</TD>' % total2)
        out.write('</TR>\n')
    total = total1 + total2
    out.write('<TR><TH style="text-align: left">Total</TH>')
    out.write('<TH style="text-align: right">%d</TH></TR>\n' % total)
    out.write('</TABLE>\n')
    return total

def make_package_report(c, biocrepo, pkg, main_page_file, main_page_title,
                        with_IPs=False):
    package_page = '%s.html' % pkg
    out = open(package_page, 'w')
    biocrepo_label = stats_config.biocrepo2label[biocrepo]
    title = 'Download stats for %s package %s' % (biocrepo_label, pkg)
    write_top_asHTML(out, title, '../main.css')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "../" + main_page_file, main_page_title)
    out.write('<H1 style="text-align: center;">%s</H1>\n' % title)
    write_timestamp_asHTML(out)
    write_links_to_package_home(out, pkg)
    sql_where = "biocrepo='%s' AND package='%s'" % (biocrepo, pkg)
    total1 = write_DownloadsPerMonth_TABLE(c, out, pkg, sql_where,
                                           pkg + '.png')
    if with_IPs:
        total2 = write_DownloadsPerIP_TABLE(c, out, pkg, sql_where, 50)
        #if total1 != total2:
        #    print 'make_package_report(): total1 != total2'
        #    sys.exit("==> EXIT")
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return total1

def make_package_reports(c, biocrepo, main_page_file, main_page_title):
    biocrepo_subdir = stats_config.biocrepo2subdir[biocrepo]
    os.mkdir(biocrepo_subdir)
    os.chdir(biocrepo_subdir)
    pkgs = SQL_getDistinctPackages(c, biocrepo)
    pkg_to_Y = {}
    for pkg in pkgs:
        pkg_to_Y[pkg] = make_package_report(c, biocrepo, pkg,
                                            main_page_file, main_page_title)
    os.chdir('..')
    return pkg_to_Y

def write_TotalDownloadsPerPkg_TABLE(out, biocrepo, pkgs, pkg_to_Y,
                                     by_rank=False, n=None):
    if by_rank:
        pkgs.sort(lambda u, v: pkg_to_Y[v] - pkg_to_Y[u])
    else:
        pkgs.sort(lambda u, v: cmp(string.lower(u), string.lower(v)))
    if n != None:
        pkgs = pkgs[0:n]
    ncol = 3
    nrow = (len(pkgs) + ncol - 1) / ncol
    out.write('<TABLE class="totaldlperpkg"><TR>\n')
    for j in range(ncol):
        out.write('<TD style="vertical-align: top; width:300px;">\n')
        if j * nrow < len(pkgs):
            out.write('<TABLE>\n')
            for i in range(nrow):
                p = j * nrow + i
                if p >= len(pkgs):
                    break
                out.write('<TR class="totaldlperpkg">')
                out.write('<TD style="width:25px; text-align: right">')
                if by_rank:
                    out.write(str(p + 1))
                out.write('</TD>')
                pkgname_html = pkg = pkgs[p]
                biocrepo_subdir = stats_config.biocrepo2subdir[biocrepo]
                package_page_href = '%s/%s.html' % (biocrepo_subdir, pkg)
                if pkg in stats_config.bioclite_pkgs:
                    pkgname_html = '<B>%s</B>' % pkgname_html
                out.write('<TD><A HREF="%s">%s&nbsp;(%d)</A></TD>' % \
                          (package_page_href, pkgname_html, pkg_to_Y[pkg]))
                out.write('</TR>\n')
            out.write('</TABLE>\n')
        out.write('</TD>\n')
    out.write('</TR></TABLE>\n')
    return

def write_AlphabeticalIndex(out, biocrepo, pkg_to_Y):
    letter_to_pkg = {}
    pkgs = pkg_to_Y.keys()
    ## Group packages per first letter
    for pkg in pkgs:
        first_letter = pkg[0].upper()
        if letter_to_pkg.has_key(first_letter):
            letter_to_pkg[first_letter].append(pkg)
        else:
            letter_to_pkg[first_letter] = [pkg]
    ## Write stats for each group
    letters = letter_to_pkg.keys()
    letters.sort(lambda u, v: cmp(string.lower(u), string.lower(v)))
    for letter in letters:
        out.write('<H3 style="font-family: monospace; font-size: larger;">%s</H3>\n' % letter)
        write_TotalDownloadsPerPkg_TABLE(out, biocrepo,
                                         letter_to_pkg[letter], pkg_to_Y)
    return

