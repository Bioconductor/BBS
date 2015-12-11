#! /usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Apr 23, 2010
###

import sys
import os
import time
import shutil
import re
import fnmatch

import bbs.fileutils
import bbs.parse
import bbs.jobs
import bbs.html
import BBScorevars
import BBSvars
import BBSreportutils


class LeafReportReference:
    def __init__(self, pkg, node_hostname, node_id, stagecmd):
        self.pkg = pkg
        self.node_hostname = node_hostname
        self.node_id = node_id
        self.stagecmd = stagecmd

def wopen_leafreport_input_file(pkg, node_id, stagecmd, file, catch_HTTPerrors=False):
    if pkg:
        file = "%s.%s-%s" % (pkg, stagecmd, file)
    rdir = BBScorevars.nodes_rdir.subdir('%s/%s' % (node_id, stagecmd))
    return rdir.WOpen(file, catch_HTTPerrors=catch_HTTPerrors)

STATUS_SUMMARY = {}

def update_STATUS_SUMMARY(pkg, node_id, stagecmd, status):
    if not STATUS_SUMMARY.has_key(node_id):
        STATUS_SUMMARY[node_id] = { 'install':  (0, 0, 0, 0, 0), \
                                    'buildsrc': (0, 0, 0, 0, 0), \
                                    'checksrc': (0, 0, 0, 0, 0), \
                                    'buildbin': (0, 0, 0, 0, 0) }
    x = STATUS_SUMMARY[node_id][stagecmd]
    x0 = x[0]
    x1 = x[1]
    x2 = x[2]
    x3 = x[3]
    x4 = x[4]
    if status == "TIMEOUT":
        x0 += 1
    if status == "ERROR":
        x1 += 1
    if status == "WARNINGS":
        x2 += 1
    if status == "OK":
        x3 += 1
    if status == "NotNeeded":
        x4 += 1
    STATUS_SUMMARY[node_id][stagecmd] = (x0, x1, x2, x3, x4)
    return

def make_STATUS_SUMMARY(allpkgs):
    for pkg in allpkgs:
        for node in BBSreportutils.supported_nodes(pkg):
            # INSTALL status
            stagecmd = 'install'
            status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
            update_STATUS_SUMMARY(pkg, node.id, stagecmd, status)
            # BUILD status
            stagecmd = 'buildsrc'
            status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
            update_STATUS_SUMMARY(pkg, node.id, stagecmd, status)
            skipped_is_OK = status in ["TIMEOUT", "ERROR"]
            # CHECK status
            stagecmd = 'checksrc'
            if skipped_is_OK:
                status = "skipped"
            else:
                status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
            update_STATUS_SUMMARY(pkg, node.id, stagecmd, status)
            if BBSreportutils.is_doing_buildbin(node):
                # BUILD BIN status
                stagecmd = 'buildbin'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
                update_STATUS_SUMMARY(pkg, node.id, stagecmd, status)
    return


##############################################################################
### HTMLization
##############################################################################

def writeThinRowSeparator_asTR(out, tr_class=None):
    if tr_class:
        tr_class = ' class="%s"' % tr_class
    else:
        tr_class = '';
    out.write('<TR%s><TD COLSPAN="8" style="height: 4pt; background: inherit;"></TD></TR>\n' % tr_class)
    return

### From internal stage command to stage HTML label
stagecmd2label = {
    'install':  "INSTALL",
    'buildsrc': "BUILD",
    'checksrc': "CHECK",
    'buildbin': "BUILD BIN"
}

def get_alphabet_dispatcher_asHTML(current_letter=None, href=""):
    html = ''
    for i in range(65,91):
        letter = chr(i)
        html_letter = '<A href="%s#%s">%s</A>' % (href, letter, letter)
        if letter == current_letter:
            html_letter = '<B>[%s]</B>' % html_letter
        else:
            html_letter = '&nbsp;%s&nbsp;' % html_letter
        html += html_letter
    return html

def get_pkgname_asHTML(pkg):
    if BBScorevars.mode == "cran":
        url = "http://cran.fhcrc.org/web/packages/%s/" % pkg
    else:
        version_string = BBSreportutils.bioc_version
        if BBScorevars.mode == "data-experiment":
            repo = "data/experiment"
        else:
            repo = "bioc"
        url = "/packages/%s/%s/html/%s.html" % (version_string, repo, pkg)
    return '<A href="%s">%s</A>' % (url, pkg)


##############################################################################
### svn info HTMLization
##############################################################################

### Top-level svn info
def write_svn_info_asHTML(out, key):
    val = BBSreportutils.get_svn_info(None, key)
    key = ' - %s' % key
    key = key.replace(' ', '&nbsp;')
    out.write('%s: <SPAN class="svn_info">%s</SPAN><BR>\n' % (key, val))
    return

def write_svn_Changelog_asTD(out, url, pkg):
    if pkg != None:
        url = '%s/%s' % (url, pkg)
    out.write('<TD class="svn_info"><A href="%s">Bioconductor Changelog</A></TD>' % url)
    return

def write_svn_SnapshotDate_asTD(out):
    key = 'Snapshot Date'
    val = BBSreportutils.get_svn_info(None, key)
    key = key.replace(' ', '&nbsp;')
    val = val.replace(' ', '&nbsp;')
    val = '%s:&nbsp;<SPAN class="svn_info">%s</SPAN>' % (key, val)
    out.write('<TD class="svn_info">%s</TD>' % val)
    return

def write_svn_URL_asTD(out, pkg):
    key = 'URL'
    val = BBSreportutils.get_svn_info(pkg, key)
    val = '%s:&nbsp;<SPAN class="svn_info">%s</SPAN>' % (key, val)
    out.write('<TD class="svn_info">%s</TD>' % val)
    return

def write_svn_LastChangedRev_asTD(out, pkg, with_Revision=False):
    key = 'Last Changed Rev'
    val = BBSreportutils.get_svn_info(pkg, key)
    key = key.replace(' ', '&nbsp;')
    val = '%s:&nbsp;<SPAN class="svn_info">%s</SPAN>' % (key, val)
    if with_Revision:
        key2 = 'Revision'
        val2 = BBSreportutils.get_svn_info(pkg, key2)
        val = '%s / %s:&nbsp;<SPAN class="svn_info">%s</SPAN>' % (val, key2, val2)
    out.write('<TD class="svn_info">%s</TD>' % val)
    return

def write_svn_LastChangedDate_asTD(out, pkg, full_line=True):
    key = 'Last Changed Date'
    val = BBSreportutils.get_svn_info(pkg, key)
    if not full_line:
        val = ' '.join(val.split(' ')[0:3])
    key = key.replace(' ', '&nbsp;')
    val = val.replace(' ', '&nbsp;')
    val = '%s:&nbsp;<SPAN class="svn_info">%s</SPAN>' % (key, val)
    out.write('<TD class="svn_info">%s</TD>' % val)
    return

def write_svn_info_for_pkg_asTABLE(out, pkg, full_info=False):
    out.write('<TABLE class="svn_info">')
    if 'BBS_SVNCHANGELOG_URL' in os.environ:
        url = os.environ['BBS_SVNCHANGELOG_URL']
        out.write('<TR>')
        write_svn_Changelog_asTD(out, url, pkg)
        out.write('</TR>')
    if full_info:
        out.write('<TR>')
        write_svn_SnapshotDate_asTD(out)
        out.write('</TR>')
        out.write('<TR>')
        write_svn_URL_asTD(out, pkg)
        out.write('</TR>')
    out.write('<TR>')
    write_svn_LastChangedRev_asTD(out, pkg, True)
    out.write('</TR>')
    out.write('<TR>')
    write_svn_LastChangedDate_asTD(out, pkg, full_info)
    out.write('</TR>')
    out.write('</TABLE>')
    return


##############################################################################
### leaf-report and mainrep tables
##############################################################################

def nodeOSArch_asSPAN(node):
    return '<SPAN style="font-size: smaller;">%s&nbsp;/&nbsp;%s</SPAN>' % (node.os_html, node.arch)

def write_node_spec_asTD(out, node, spec_html, leafreport_ref):
    if leafreport_ref != None and node.id == leafreport_ref.node_id:
        out.write('<TD class="node %s current"' % node.hostname.replace(".", "_"))
    else:
        out.write('<TD class="node %s"' % node.hostname.replace(".", "_"))
    out.write(' style="text-align: left">%s&nbsp;</TD>' % spec_html)
    return

def status_asSPAN(status):
    return '<SPAN class="%s">&nbsp;%s&nbsp;</SPAN>' % (status, status)

def write_pkg_status_asTD(out, pkg, node, stagecmd, leafreport_ref, style=None):
    #print "  %s %s %s" % (pkg, node.id, stagecmd)
    status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
    if status == "skipped":
        status_html = status_asSPAN(status)
    else:
        if leafreport_ref != None:
            pkgdir = "."
        else:
            pkgdir = pkg
        leafreport_rURL = BBSreportutils.get_leafreport_rURL(pkgdir, node.id, stagecmd)
        status_html = '<A href="%s">%s</A>' % (leafreport_rURL, status_asSPAN(status))
        if leafreport_ref != None \
           and pkg == leafreport_ref.pkg \
           and node.id == leafreport_ref.node_id \
           and stagecmd == leafreport_ref.stagecmd:
            status_html = '[%s]' % status_html
    if style == None:
        style = ""
    else:
        style = ' style="%s"' % style
    out.write('<TD class="status %s %s"%s>%s</TD>' % (node.hostname, stagecmd, style, status_html))
    return

### Produces 5 TDs (4 of the same width + 1 narrow one on the right)
def write_pkg_5stagelabels_as5TDs(out, extra_style=""):
    for stagecmd in ["install", "buildsrc", "checksrc", "buildbin"]:
        out.write('<TD class="stagecmd %s" style="text-align: center%s">' % \
                  (stagecmd, extra_style))
        out.write(stagecmd2label[stagecmd])
        out.write('</TD>')
    out.write('<TD style="width:11px;"></TD>')
    return

def write_pkg_propagation_status_asTD(out, pkg, node):
    status = BBSreportutils.get_propagation_status_from_db(pkg, node.hostname)
    if (status is None):
        out.write('<TD class="status %s" style="width: 11px;"></TD>' % node.hostname.replace(".", "_"))
        return()
    if (status.startswith("YES")):
        color = "Green"
    elif (status.startswith("NO")):
        color = "Red"
    else: # "UNNEEDED"
        color = "Blue"
    path = ""
    if "/" in out.name:
        path = "../"
    out.write('<TD class="status %s" style="width: 11px;"><IMG border="0" width="10" height="10" alt="%s" title="%s" src="%s120px-%s_Light_Icon.svg.png"></TD>' \
        % (node.hostname.replace(".", "_"), status, status, path, color))


### Produces 5 TDs
def write_pkg_5statuses_as5TDs(out, pkg, node, leafreport_ref, style=None):
    if BBSreportutils.is_supported(pkg, node):
        write_pkg_status_asTD(out, pkg, node, 'install', leafreport_ref, style)
        write_pkg_status_asTD(out, pkg, node, 'buildsrc', leafreport_ref, style)
        write_pkg_status_asTD(out, pkg, node, 'checksrc', leafreport_ref, style)
        if BBSreportutils.is_doing_buildbin(node):
            write_pkg_status_asTD(out, pkg, node, 'buildbin', leafreport_ref, style)
        else:
            out.write('<TD class="node %s"></TD>' % node.hostname.replace(".", "_"))
        write_pkg_propagation_status_asTD(out, pkg, node)
    else:
        out.write('<TD COLSPAN="5" class="node %s"><I>' % node.hostname.replace(".", "_"))
        sep = '...'
        NOT_SUPPORTED_string = sep + 3 * ('NOT SUPPORTED' + sep)
        out.write(NOT_SUPPORTED_string.replace(' ', '&nbsp;'))
        out.write('</I></TD>')
    return

### Produces 2 full TRs ("full TR" = TR with 8 TDs)
def write_pkg_index_as2fullTRs(out, current_letter):
    ## FH: Need the abc class to blend out the alphabetical selection when
    ## "ok" packages are unselected.
    writeThinRowSeparator_asTR(out, "abc")
    out.write('<TR class="abc"><TD COLSPAN="8" style="background: inherit; font-family: monospace;">')
    out.write('<A name="%s"><B style="font-size: larger;">%s</B></A>' % (current_letter, current_letter))
    out.write('&nbsp;%s' % get_alphabet_dispatcher_asHTML(current_letter))
    out.write('</TD></TR>\n')
    return

def statuses2classes(statuses):
    classes = ""
    if "TIMEOUT" in statuses:
        classes += " timeout"  # string concatenation
    if "ERROR" in statuses:
        classes += " error"
    if "WARNINGS" in statuses:
        classes += " warnings"
    ## A package is tagged with the "ok" class if it's not tagged with any of
    ## the "timeout", "error" or "warnings" class. Note that this means that
    ## a package could end up being tagged with the "ok" class even if it
    ## doesn't have any OK in 'statuses' (e.g. if it's unsupported on all
    ## platforms).
    if classes == "":
        classes = "ok"
    return classes

### Produces full TRs ("full TR" = TR with 8 TDs)
def write_pkg_allstatuses_asfullTRs(out, pkg, pkg_pos, nb_pkgs, leafreport_ref):
    if leafreport_ref == None and pkg_pos % 2 == 0:
        classes = "even"
    else:
        classes = "odd"
    statuses = BBSreportutils.get_distinct_statuses_from_db(pkg)
    classes += " " + statuses2classes(statuses)
    out.write('<TR class="%s header">' % classes)
    out.write('<TD>Package <B>%d</B>/%d</TD>' % (pkg_pos, nb_pkgs))
    out.write('<TD style="text-align: left">Hostname</TD>')
    out.write('<TD style="text-align: left; width: 290px">OS&nbsp;/&nbsp;Arch</TD>')
    if leafreport_ref == None:
        extra_style = ""
    else:
        extra_style = "; width: 96px"
    write_pkg_5stagelabels_as5TDs(out, extra_style)
    out.write('</TR>\n')
    nb_nodes = len(BBSreportutils.NODES)
    is_first = True
    for node in BBSreportutils.NODES:
        out.write('<TR class="%s">' % classes)
        if is_first:
            pkgname_html = get_pkgname_asHTML(pkg)
            version = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Version')
            maintainer = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Maintainer')
            out.write('<TD ROWSPAN="%d" style="padding-left: 12px; vertical-align: top;">' \
                      % nb_nodes)
            #out.write('<H3>%s</H3>' % pkgname_html)
            #out.write('<H4>%s</H4>' % version)
            #out.write('<B><SPAN style="font-size: larger;">%s</SPAN>&nbsp;%s</B><BR>' % (pkgname_html, version))
            out.write('<B>%s&nbsp;%s</B>' % (pkgname_html, version))
            out.write('<BR>%s' % maintainer)
            if BBSvars.MEAT0_type == 1:
                out.write('<BR>')
                write_svn_info_for_pkg_asTABLE(out, pkg, leafreport_ref != None)
            out.write('</TD>')
            is_first = False
        write_node_spec_asTD(out, node, '<I>%s</I>' % node.id, leafreport_ref)
        write_node_spec_asTD(out, node, nodeOSArch_asSPAN(node), leafreport_ref)
        #if leafreport_ref == None:
        #    style = None
        #else:
        #    style = "font-size: smaller"
        #write_pkg_5statuses_as5TDs(out, pkg, node, leafreport_ref, style)
        write_pkg_5statuses_as5TDs(out, pkg, node, leafreport_ref)
        out.write('</TR>\n')
    return

def write_summary_TD(out, node, stagecmd):
    stats = STATUS_SUMMARY[node.id][stagecmd]
    html = '<TABLE class="summary"><TR>'
    html += '<TD class="summary %s">%d</TD>' % ("TIMEOUT", stats[0])
    html += '<TD class="summary %s">%d</TD>' % ("ERROR", stats[1])
    if stagecmd == 'checksrc':
        html += '<TD class="summary %s">%d</TD>' % ("WARNINGS", stats[2])
    html += '<TD class="summary %s">%d</TD>' % ("OK", stats[3])
    if stagecmd == 'install':
        html += '<TD class="summary %s">%d</TD>' % ("NotNeeded", stats[4])
    html += '</TR></TABLE>'
    #out.write('<TD class="status %s %s">%s</TD>' % (node.hostname.replace(".", "_"), stagecmd, html))
    out.write('<TD>%s</TD>' % html)
    return

### Produces full TRs ("full TR" = TR with 8 TDs)
def write_summary_asfullTRs(out, nb_pkgs, current_node=None):
    out.write('<TR class="summary header">')
    out.write('<TD COLSPAN="2" style="background: inherit;">SUMMARY</TD>')
    out.write('<TD style="text-align: left; width: 290px">OS&nbsp;/&nbsp;Arch</TD>')
    write_pkg_5stagelabels_as5TDs(out)
    out.write('</TR>\n')
    nb_nodes = len(BBSreportutils.NODES)
    for node in BBSreportutils.NODES:
        if current_node == node.id:
            out.write('<TR class="summary %s current">\n' % node.hostname.replace(".", "_"))
        else:
            out.write('<TR class="summary %s">\n' % node.hostname.replace(".", "_"))
        node_id_html = '<I>%s</I>' % node.id
        if nb_nodes != 1:
            node_index_file = '%s-index.html' % node.id
            node_id_html = '<A href="%s">%s</A>' % (node_index_file, node_id_html)
            if current_node == node.id:
                node_id_html = '[%s]' % node_id_html
        out.write('<TD COLSPAN="2" style="padding-left: 12px;">%s</TD>\n' % node_id_html)
        out.write('<TD>%s&nbsp;</TD>' % nodeOSArch_asSPAN(node))
        write_summary_TD(out, node, 'install')
        write_summary_TD(out, node, 'buildsrc')
        write_summary_TD(out, node, 'checksrc')
        if BBSreportutils.is_doing_buildbin(node):
            write_summary_TD(out, node, 'buildbin')
        else:
            out.write('<TD></TD>')
        out.write('<TD style="width:11px;"></TD>')
        out.write('</TR>\n')
    return

### When leafreport_ref is specified, then the mini table for this leaf-report
### only is generated.
def write_mainreport_asTABLE(out, allpkgs, leafreport_ref=None):
    full_table = not leafreport_ref
    nb_pkgs = len(allpkgs)
    out.write('<TABLE class="mainrep">\n')
    if full_table:
        write_summary_asfullTRs(out, nb_pkgs)
    pkg_pos = 0
    current_letter = None
    for pkg in allpkgs:
        pkg_pos += 1
        first_letter = pkg[0:1].upper()
        if first_letter != current_letter:
            current_letter = first_letter
            if full_table and not no_alphabet_dispatch:
                write_pkg_index_as2fullTRs(out, current_letter)
        if full_table or pkg == leafreport_ref.pkg:
            write_pkg_allstatuses_asfullTRs(out, pkg, pkg_pos, nb_pkgs, leafreport_ref)
    out.write('</TABLE>\n')
    return


##############################################################################
### Compact report (the compact layout is used for the node-specific reports).
##############################################################################

### Produces a full TR ("full TR" = TR with 8 TDs)
def write_compactreport_header_asfullTR(out):
    ## Using the abc class here too to blend out the alphabetical selection +
    ## this header when "ok" packages are unselected.
    out.write('<TR class="header abc">')
    out.write('<TD style="width: 50px;"></TD>')
    out.write('<TD style="text-align: left; padding-left: 12px;">Package</TD>')
    out.write('<TD style="text-align: left">Maintainer</TD>')
    write_pkg_5stagelabels_as5TDs(out)
    out.write('</TR>\n')
    return

### Produces a full TR ("full TR" = TR with 8 TDs)
def write_compactreport_fullTR(out, pkg, node, pkg_pos, nb_pkgs, leafreport_ref):
    if pkg_pos % 2 == 0 and not leafreport_ref:
        classes = "even"
    else:
        classes = "odd"
    statuses = BBSreportutils.get_distinct_statuses_from_db(pkg, [node])
    classes += " " + statuses2classes(statuses)
    out.write('<TR class="%s">' % classes)
    out.write('<TD class="header" style="text-align: right;"><B>%d</B>/%d</TD>' % (pkg_pos, nb_pkgs))
    out.write('<TD style="text-align: left; padding-left: 12px;">')
    version = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Version')
    out.write('<B>%s</B>&nbsp;<B>%s</B>' % (get_pkgname_asHTML(pkg), version))
    out.write('</TD>')
    maintainer = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Maintainer')
    out.write('<TD style="text-align: left">%s</TD>' % maintainer)
    write_pkg_5statuses_as5TDs(out, pkg, node, leafreport_ref)
    out.write('</TR>\n')
    return

### Same as write_mainreport_asTABLE(), but can be used to display results
### for a single node with a more compact layout.
def write_compactreport_asTABLE(out, node, allpkgs, leafreport_ref=None):
    full_table = not leafreport_ref
    nb_pkgs = len(allpkgs)
    out.write('<TABLE class="mainrep">\n')
    if full_table:
        write_summary_asfullTRs(out, nb_pkgs, node.id)
        writeThinRowSeparator_asTR(out)
        if no_alphabet_dispatch:
            write_compactreport_header_asfullTR(out)
    pkg_pos = 0
    current_letter = None
    for pkg in allpkgs:
        pkg_pos += 1
        first_letter = pkg[0:1].upper()
        if first_letter != current_letter:
            current_letter = first_letter
            if full_table and not no_alphabet_dispatch:
                write_pkg_index_as2fullTRs(out, current_letter)
                write_compactreport_header_asfullTR(out)
        if full_table or pkg == leafreport_ref.pkg:
            write_compactreport_fullTR(out, pkg, node, pkg_pos, nb_pkgs, leafreport_ref)
    out.write('</TABLE>\n')
    return


##############################################################################
### leaf-reports
##############################################################################

def write_top_asHTML(out, title, css_file=None, js_file=None):
    out.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"')
    out.write(' "http://www.w3.org/TR/html4/loose.dtd">\n')
    out.write('<HTML>\n')
    out.write('<HEAD>\n')
    out.write('<script language="javascript">\n')
    out.write('if (!/\.html$|\/$|#/.test(window.location.href))\n')
    out.write('  window.location.href = window.location.href + "/";\n')
    out.write('</script>\n')
    out.write('<META http-equiv="Content-Type" content="text/html; charset=UTF-8">\n')
    out.write('<TITLE>%s</TITLE>\n' % title)
    if css_file:
        out.write('<LINK rel="stylesheet" href="%s" type="text/css">\n' % css_file)
    if js_file:
        out.write('<SCRIPT type="text/javascript" src="%s"></SCRIPT>\n' % js_file)
    out.write('</HEAD>\n')
    return

def write_goback_asHTML(out, href, current_letter=None):
    out.write('<TABLE style="width: 100%; border-spacing: 0px; border-collapse: collapse;"><TR>')
    out.write('<TD style="padding: 0px; text-align: left;">')
    out.write('<I><A href="%s">Back to the &quot;%s&quot;</A></I>' % (href, main_page_title))
    out.write('</TD>')
    if not no_alphabet_dispatch and current_letter != None:
        out.write('<TD style="padding: 0px; text-align: right; font-family: monospace;">')
        out.write(get_alphabet_dispatcher_asHTML(current_letter, href))
        out.write('</TD>')
    out.write('</TR></TABLE>\n')
    return

def write_motd_asTABLE(out):
    if not 'BBS_REPORT_MOTD' in os.environ:
        return
    motd = os.environ['BBS_REPORT_MOTD']
    if motd == "":
        return
    out.write('<TABLE class="motd">')
    out.write('<TR><TD>%s</TD></TR>' % bbs.html.encodeHTMLentities(motd, 'utf_8')) # untrusted
    out.write('</TABLE>\n')
    return

def make_PkgReportLandingPage(leafreport_ref, allpkgs):
    pkg = leafreport_ref.pkg
    title = '%s: BUILD/CHECK reports for %s' % (BBSreportutils.get_build_label(), pkg)
    date = bbs.jobs.currentDateString()
    out_rURL = '%s/index.html' % pkg
    out = open(out_rURL, 'w')

    ## Start writing the HTML page
    write_top_asHTML(out, title, '../report.css')
    out.write('<BODY>\n')
    current_letter = pkg[0:1].upper()
    write_goback_asHTML(out, "../index.html", current_letter)
    out.write('<BR>\n')
    out.write('<H1 style="text-align: center;">%s</H1>\n' % title)
    out.write('<P style="text-align: center;">\n')
    out.write('<I>This page was generated on %s.</I>\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)
    write_mainreport_asTABLE(out, allpkgs, leafreport_ref)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

def write_Summary_to_LeafReport(out, node_hostname, pkg, node_id, stagecmd):
    out.write('<H3>Summary</H3>\n')
    out.write('<DIV class="%s" style="margin-left: 12px;">\n' % node_hostname.replace(".", "_"))
    dcf = wopen_leafreport_input_file(pkg, node_id, stagecmd, "summary.dcf")
    out.write('<TABLE>\n')
    while True:
        field_val = bbs.parse.getNextDcfFieldVal(dcf, True)
        if not field_val:
            break
        if field_val[0] == 'Status':
            field_val = (field_val[0], status_asSPAN(field_val[1]))
        out.write('<TR><TD><B>%s</B>: %s</TD></TR>\n' % field_val)
    out.write('</TABLE>\n')
    dcf.close()
    out.write('</DIV>\n')
    return

def write_Command_output_to_LeafReport(out, node_hostname,
                                       pkg, node_id, stagecmd):
    out.write('<H3>Command output</H3>\n')
    out.write('<DIV class="%s" style="margin-left: 12px;">\n' % node_hostname.replace(".", "_"))
    f = wopen_leafreport_input_file(pkg, node_id, stagecmd, "out.txt")
    encoding = BBScorevars.getNodeSpec(node_hostname, 'encoding')
    out.write('<PRE style="font-size: smaller; padding: 2px;">\n')
    unit_test_failure_regex = re.compile("^Running the tests in .(.*). failed[.]")
    unit_test_failed = False
    for line in f:
        if(unit_test_failure_regex.match(line)):
            unit_test_failed = True
        try:
            html_line = bbs.html.encodeHTMLentities(line, encoding) # untrusted
        except:
            html_line = line
        try:
            out.write(html_line)
        except Exception:
            out.write(html_line.encode("utf-8"))
    out.write('</PRE>\n')
    f.close()
    out.write('</DIV>\n')

    def write_file_output(filename, filehandle=None):
        out.write('<P>%s:</P>\n' % filename)
        out.write('<DIV class="%s" style="margin-left: 12px;">\n' % node_hostname.replace(".", "_"))
        out.write('<PRE style="font-size: smaller;">\n')
        for line in filehandle:
            out.write(bbs.html.encodeHTMLentities(line, encoding)) # untrusted
        out.write('</PRE>\n')
        out.write('</DIV>')

    if stagecmd == "checksrc" and unit_test_failed: # unit test output
        fullpath = "%s/nodes/%s/%s" % (os.environ['BBS_CENTRAL_RDIR'], 
            node_id, stagecmd)
        for folder, subs, files in os.walk(fullpath):
            for filename in files:
                if fnmatch.fnmatch(filename, "*.Rout.fail"):
                    with open(os.path.join(folder, filename), "r") as fh:
                        write_file_output(filename, fh)

    if stagecmd == "checksrc":
        file = '%s.Rcheck/00install.out' % pkg
        f = wopen_leafreport_input_file(None, node_id, stagecmd, file, catch_HTTPerrors=True)
        if f != None:
            out.write('<P>%s:</P>\n' % file)
            out.write('<DIV class="%s" style="margin-left: 12px;">\n' % node_hostname.replace(".", "_"))
            out.write('<PRE style="font-size: smaller;">\n')
            for line in f:
                out.write(bbs.html.encodeHTMLentities(line, encoding)) # untrusted
            out.write('</PRE>\n')
            out.write('</DIV>')
            f.close()
        files = ['%s.Rcheck/%s-Ex.timings' % (pkg, pkg),
            '%s.Rcheck/examples_i386/%s-Ex.timings' % (pkg, pkg),
            '%s.Rcheck/examples_x64/%s-Ex.timings' % (pkg, pkg)]
        for file in files:
            f = wopen_leafreport_input_file(None, node_id, stagecmd, file, catch_HTTPerrors=True)
            if f != None:
                out.write('<P>%s:</P>\n' % file)
                out.write('<DIV class="%s" style="margin-left: 12px;">\n' % node_hostname.replace(".", "_"))
                out.write('<TABLE style="font-size: smaller;">\n')
                for line in f:
                    out.write('<TR><TD>')
                    out.write(line.replace('\t', '</TD><TD style="text-align: right;">'))
                    out.write('</TD><TR>\n')
                out.write('</TABLE>\n')
                out.write('</DIV>')
                f.close()
    return

def make_LeafReport(leafreport_ref, allpkgs):
    pkg = leafreport_ref.pkg
    node_hostname = leafreport_ref.node_hostname
    node_id = leafreport_ref.node_id
    stagecmd = leafreport_ref.stagecmd
    title = '%s: %s report for %s on %s' % (BBSreportutils.get_build_label(), stagecmd2label[stagecmd], pkg, node_id)
    leafreport_rURL = BBSreportutils.get_leafreport_rURL(pkg, node_id, stagecmd)
    date = bbs.jobs.currentDateString()
    out = open(leafreport_rURL, 'w')

    ## Start writing the HTML page
    write_top_asHTML(out, title, '../report.css')
    out.write('<BODY>\n')
    current_letter = pkg[0:1].upper()
    write_goback_asHTML(out, "../index.html", current_letter)
    out.write('<BR>\n')
    out.write('<H1 style="text-align: center;">%s</H1>\n' % title)
    out.write('<P style="text-align: center;">\n')
    out.write('<I>This page was generated on %s.</I>\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)
    write_mainreport_asTABLE(out, allpkgs, leafreport_ref)
    #if len(BBSreportutils.NODES) != 1:
    #    write_mainreport_asTABLE(out, allpkgs, leafreport_ref)
    #else:
    #    write_compactreport_asTABLE(out, BBSreportutils.NODES[0], allpkgs, leafreport_ref)
    out.write('<HR>\n')

    status = BBSreportutils.get_status_from_db(pkg, node_id, stagecmd)
    if stagecmd == "install" and status == "NotNeeded":
        out.write('<DIV class="%s" style="margin-left: 12px;">\n' % node_hostname.replace(".", "_"))
        out.write('REASON FOR NOT INSTALLING: no other package that will ')
        out.write('be built and checked on this platform needs %s' % pkg)
        out.write('</DIV>\n')
    else:
        ## Summary
        write_Summary_to_LeafReport(out, node_hostname,
                                    pkg, node_id, stagecmd)
        out.write('<HR>\n')
        ## Command output
        write_Command_output_to_LeafReport(out, node_hostname,
                                           pkg, node_id, stagecmd)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

def make_node_LeafReports(allpkgs, node):
    print "BBS> [make_node_LeafReports] Node %s: BEGIN..." % node.id
    for pkg in BBSreportutils.supported_pkgs(node):
        # INSTALL leaf-report
        stagecmd = "install"
        status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
        if status != "skipped":
            leafreport_ref = LeafReportReference(pkg, node.hostname, node.id, stagecmd)
            make_LeafReport(leafreport_ref, allpkgs)
        # BUILD leaf-report
        stagecmd = "buildsrc"
        status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
        if status != "skipped":
            leafreport_ref = LeafReportReference(pkg, node.hostname, node.id, stagecmd)
            make_LeafReport(leafreport_ref, allpkgs)
        # CHECK leaf-report
        stagecmd = "checksrc"
        status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
        if status != "skipped":
            leafreport_ref = LeafReportReference(pkg, node.hostname, node.id, stagecmd)
            make_LeafReport(leafreport_ref, allpkgs)
        if BBSreportutils.is_doing_buildbin(node):
            # BUILD BIN leaf-report
            stagecmd = "buildbin"
            status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
            if status != "skipped":
                leafreport_ref = LeafReportReference(pkg, node.hostname, node.id, stagecmd)
                make_LeafReport(leafreport_ref, allpkgs)
    print "BBS> [make_node_LeafReports] Node %s: END" % node.id
    return

def make_all_LeafReports(allpkgs):
    print "Current workding dir '%s'" % os.getcwd()
    for pkg in allpkgs:
        try:
            os.mkdir(pkg)
        except:
            print "mkdir failed in make_all_LeaveReports '%s'" % pkg
            continue
        leafreport_ref = LeafReportReference(pkg, None, None, None)
        make_PkgReportLandingPage(leafreport_ref, allpkgs)
    for node in BBSreportutils.NODES:
        make_node_LeafReports(allpkgs, node)
    return


##############################################################################
### Main page: HTML stuff above main table
##############################################################################

def write_BioC_mainpage_head_asHTML(out):
    title = "%s: %s" % (BBSreportutils.get_build_label(), main_page_title)
    date = bbs.jobs.currentDateString()
    ## Start writing the HTML page
    write_top_asHTML(out, title, 'report.css', 'report.js')
    ## FH: Initialize the checkboxes when page is (re)loaded
    out.write('<BODY  onLoad="initialize();">\n')
    out.write('<H1 style="text-align: center;">%s</H1>\n' % title)
    out.write('<P style="text-align: center;">\n')
    out.write('<I>This page was generated on %s.</I>\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)
    if BBSvars.MEAT0_type == 1:
        out.write('<DIV class="svn_info">\n')
        out.write('<P>svn info</P>\n')
        write_svn_info_for_pkg_asTABLE(out, None, True)
        out.write('</DIV>\n')
    return

def write_CRAN_mainpage_head_asHTML(out):
    title = 'CRAN: %s' % main_page_title
    date = bbs.jobs.currentDateString()
    ## Start writing the HTML page
    write_top_asHTML(out, title, 'report.css', 'report.js')
    out.write('<BODY>\n')
    out.write('<H1 style="text-align: center;">%s</H1>\n' % title)
    out.write('<P style="text-align: center;">\n')
    out.write('<I>This page was generated on %s.</I>\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)
    return

def read_Rversion(Node_rdir):
    file = 'NodeInfo/R-version.txt'
    f = Node_rdir.WOpen(file)
    Rversion = f.readline()
    f.close()
    Rversion = Rversion.replace('R version ', '')
    Rversion_html = Rversion.replace(' ', '&nbsp;')
    return Rversion_html

def get_Rconfig_value_from_file(Node_rdir, var):
    file = 'NodeInfo/R-config.txt'
    dcf = Node_rdir.WOpen(file)
    val = bbs.parse.getNextDcfVal(dcf, var, True)
    dcf.close()
    if val == None:
        filepath = '%s/%s' % (Node_rdir.label, file)
        raise bbs.parse.DcfFieldNotFoundError(filepath, var)
    return val

def write_Rconfig_table_from_file(out, Node_rdir, vars):
    out.write('<TABLE class="Rconfig">\n')
    out.write('<TR>')
    out.write('<TD style="background: #CCC; width: 150px;"><I><B>R variable</B> (VAR)</I></TD>')
    out.write('<TD style="background: #CCC;"><I><B>Value</B> (\'R&nbsp;CMD&nbsp;config&nbsp;&lt;VAR&gt;\' output)</I></TD>')
    out.write('</TR>\n')
    for var in vars:
        val = get_Rconfig_value_from_file(Node_rdir, var)
        out.write('<TR><TD><B>%s</B></TD><TD>%s</TD></TR>\n' % (var, val))
    out.write('<TR>')
    out.write('<TD COLSPAN="2" style="font-size: smaller;">')
    out.write('<I>Please refer to \'R CMD config -h\' for the meaning of these variables</I>')
    out.write('</TD>')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    return

def write_SysCommandVersion_from_file(out, Node_rdir, var):
    file = 'NodeInfo/%s-version.txt' % var
    f = Node_rdir.WOpen(file, catch_HTTPerrors=True)
    if f == None:
        return
    cmd = get_Rconfig_value_from_file(Node_rdir, var)
    syscmd = '%s --version' % cmd
    out.write('<P><B>Compiler version</B> (\'%s\' output):</P>\n' % syscmd)
    out.write('<PRE style="margin-left: 12px;">\n')
    for line in f:
        out.write(line)
    f.close()
    out.write('</PRE>\n')
    return

def make_NodeInfo_page(Node_rdir, node):
    title = 'More about %s' % node.id
    NodeInfo_page_path = '%s-NodeInfo.html' % node.id
    out = open(NodeInfo_page_path, 'w')
    write_top_asHTML(out, title, 'report.css')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))

    out.write('<H1>%s</H1>' % title)
    out.write('<TABLE>\n')
    out.write('<TR><TD><B>Hostname:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.hostname)
    out.write('<TR><TD><B>OS:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.os_html)
    out.write('<TR><TD><B>Arch:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.arch)
    out.write('<TR><TD><B>Platform:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.platform)
    out.write('<TR><TD><B>R&nbsp;version:&nbsp;</B></TD><TD>%s</TD></TR>\n' % read_Rversion(Node_rdir))
    out.write('</TABLE>\n')
    out.write('<HR>\n')

    out.write('<H2>C compiler</H2>\n')
    C_vars = ['CC', 'CFLAGS', 'CPICFLAGS', 'CPP']
    write_Rconfig_table_from_file(out, Node_rdir, C_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CC')
    out.write('<HR>\n')

    out.write('<H2>C++ compiler</H2>\n')
    Cplusplus_vars = ['CXX', 'CXXFLAGS', 'CXXPICFLAGS', 'CXXCPP']
    write_Rconfig_table_from_file(out, Node_rdir, Cplusplus_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CXX')
    out.write('<HR>\n')

    out.write('<H2>C++11 compiler</H2>\n')
    Cplusplus11_vars = ['CXX1X', 'CXX1XFLAGS', 'CXX1XPICFLAGS', 'CXX1XSTD']
    write_Rconfig_table_from_file(out, Node_rdir, Cplusplus11_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CXX1X')
    out.write('<HR>\n')

    out.write('<H2>Fortran 77 compiler</H2>\n')
    Fortran77_vars = ['F77', 'FFLAGS', 'FLIBS', 'FPICFLAGS']
    write_Rconfig_table_from_file(out, Node_rdir, Fortran77_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'F77')
    out.write('<HR>\n')

    out.write('<H2>Fortran 9x compiler</H2>\n')
    Fortran9x_vars = ['FC', 'FCFLAGS', 'FCPICFLAGS']
    write_Rconfig_table_from_file(out, Node_rdir, Fortran9x_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'FC')
    out.write('<HR>\n')

    out.write('<P>More information might be added in the future...</P>\n')

    out.write('</DIV></BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return NodeInfo_page_path

### Make local copy (and rename) R-instpkgs.txt file.
### Returns the 2-string tuple containing the filename of the generated page
### and the number of installed pkgs.
def make_Rinstpkgs_page(Node_rdir, node):
    title = 'Installed R packages on %s' % node.id
    Rinstpkgs_page = '%s-R-instpkgs.html' % node.id
    out = open(Rinstpkgs_page, 'w')
    write_top_asHTML(out, title, 'report.css')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    file = 'NodeInfo/R-instpkgs.txt'
    out.write('<PRE>\n')
    f = Node_rdir.WOpen(file)
    nline = 0
    for line in f:
        out.write(line)
        nline += 1
    f.close()
    out.write('</PRE>\n')
    out.write('</DIV></BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return (Rinstpkgs_page, str(nline-1))

def write_node_specs_table(out):
    out.write('<TABLE class="node_specs">\n')
    out.write('<TR>\n')
    out.write('<TH>Hostname</TH>\n')
    out.write('<TH>OS</TH>\n')
    out.write('<TH>Arch&nbsp;(*)</TH>\n')
    out.write('<TH>Platform&nbsp;label&nbsp;(**)</TH>\n')
    out.write('<TH>R&nbsp;version</TH>\n')
    out.write('<TH style="text-align: right;">Installed&nbsp;pkgs</TH>\n')
    out.write('</TR>\n')
    nodes_rdir = BBScorevars.nodes_rdir
    for node in BBSreportutils.NODES:
        Node_rdir = nodes_rdir.subdir(node.id)
        NodeInfo_page_path = make_NodeInfo_page(Node_rdir, node)
        Rversion_html = read_Rversion(Node_rdir)
        Rinstpkgs_strings = make_Rinstpkgs_page(Node_rdir, node)
        out.write('<TR class="%s">\n' % node.hostname.replace(".", "_"))
        out.write('<TD><B><A href="%s"><I>%s</I></A></B></TD>\n' % (NodeInfo_page_path, node.id))
        out.write('<TD>%s</TD>\n' % node.os_html)
        out.write('<TD>%s</TD>\n' % node.arch)
        out.write('<TD>%s</TD>\n' % node.platform)
        out.write('<TD class="spec">%s</TD>\n' % Rversion_html)
        out.write('<TD class="spec" style="text-align: right;">')
        out.write('<A href="%s">%s</A>' % Rinstpkgs_strings)
        out.write('</TD>\n')
        out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD COLSPAN="6" style="font-size: smaller;">')
    out.write('<I>Click on any hostname to see more info about the system (e.g. compilers)')
    out.write(' &nbsp;&nbsp;&nbsp;&nbsp; ')
    out.write('(*) as reported by \'uname -p\', except on Windows and Mac OS X Mavericks')
    out.write(' &nbsp;&nbsp;&nbsp;&nbsp; ')
    out.write('(**) as reported by \'gcc -v\'</I>')
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    return

def write_glyph_table(out):
    timeout = int(BBScorevars.r_cmd_timeout / 60.0)
    out.write('<TABLE style="border-spacing: 1px; font-size: smaller;">\n')
    out.write('<TR>\n')
    out.write('<TD COLSPAN="2" style="text-align: left; font-style: italic;">')
    out.write('<B>Package STATUS</B> - ')
    out.write('Package status is indicated by one of the following glyphs:')
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;%s</TD>\n' % status_asSPAN('TIMEOUT'))
    out.write('<TD><I>INSTALL</I>, <I>BUILD</I>, <I>CHECK</I> or ')
    out.write('<I>BUILD BIN</I> of package took more than ')
    out.write('%d minutes</TD>\n' % timeout)
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;%s</TD>\n' % status_asSPAN('ERROR'))
    out.write('<TD><I>INSTALL</I>, <I>BUILD</I>, <I>CHECK</I> or ')
    out.write('<I>BUILD BIN</I> of package returned an error</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;%s</TD>\n' % status_asSPAN('WARNINGS'))
    out.write('<TD><I>CHECK</I> of package produced warnings</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;%s</TD>\n' % status_asSPAN('OK'))
    out.write('<TD><I>INSTALL</I>, <I>BUILD</I>, <I>CHECK</I> or ')
    out.write('<I>BUILD BIN</I> of package was OK</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;%s</TD>\n' % status_asSPAN('NotNeeded'))
    out.write('<TD><I>INSTALL</I> of package was not needed ')
    out.write('(click on glyph to see why)</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-%s</TD>\n' % status_asSPAN('skipped'))
    out.write('<TD><I>CHECK</I> or <I>BUILD BIN</I> of package ')
    out.write('was skipped because the <I>BUILD</I> step failed ')
    out.write('(or because something bad happened with the Build System itself)</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD COLSPAN="2" style="text-align: left;">')
    out.write('<I>Click on any glyph in the report below ')
    out.write('to see the status details (command output).</I>')
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    return

def write_propagation_glyph_table(out):
    out.write('<TABLE style="border-spacing: 1px; font-size: smaller;">\n')
    out.write('<TR>\n')
    out.write('<TD COLSPAN="2" style="text-align: left; font-style: italic;">')
    out.write('<B>Package propagation STATUS</B> - ')
    out.write('Package propagation status is indicated by one of the following glyphs:')
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;<IMG border="0" width="10px" height="10px" alt="YES" src="120px-Green_Light_Icon.svg.png"></TD>\n')
    out.write('<TD>YES: Package was propagated because it didn\'t previously exist or version was bumped</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;<IMG border="0" width="10px" height="10px" alt="NO" src="120px-Red_Light_Icon.svg.png"></TD>\n')
    out.write('<TD>NO: Package was not propagated because of a problem (impossible dependencies, or version lower than what is already propagated)</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD>&nbsp;-&nbsp;<IMG border="0" width="10px" height="10px" alt="UNNEEDED" src="120px-Blue_Light_Icon.svg.png"></TD>\n')
    out.write('<TD>UNNEEDED: Package was not propagated because it is already in the repository with this version. A version bump is required in order to propagate it</TD>\n')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    return

### FH: Create checkboxes to select display types
def write_select_status_table(out):
    out.write('<FORM action="">\n')
    out.write('<TABLE style="border-spacing: 1px; font-size: smaller;">\n')
    out.write('<TR>\n')
    out.write('<TD style="text-align: left; font-style: italic;">\n')
    out.write('Use the check boxes to show only packages with the selected status types:')
    out.write('</TD>\n')
    out.write('<TD style="width: 30px; text-align: right; vertical-align: middle;">')
    out.write('<INPUT type="checkbox" checked id="timeout" onClick="toggle(\'timeout\')">')
    out.write('</TD>')
    out.write('<TD style="text-align: left; vertical-align: middle;">')
    out.write(status_asSPAN('TIMEOUT'))
    out.write('</TD>\n')
    out.write('<TD style="width: 30px; text-align: right; vertical-align: middle;">')
    out.write('<INPUT type="checkbox" checked id="error" onClick="toggle(\'error\')">')
    out.write('</TD>')
    out.write('<TD style="text-align: left; vertical-align: middle;">')
    out.write(status_asSPAN('ERROR'))
    out.write('</TD>\n')
    out.write('<TD style="width: 30px; text-align: right; vertical-align: middle;">')
    out.write('<INPUT type="checkbox" checked id="warnings" onClick="toggle(\'warnings\')">')
    out.write('</TD>')
    out.write('<TD style="text-align: left; vertical-align: middle;">')
    out.write(status_asSPAN('WARNINGS'))
    out.write('</TD>\n')
    out.write('<TD style="width: 30px; text-align: right; vertical-align: middle;">')
    out.write('<INPUT type="checkbox" checked id="ok" onClick="toggle(\'ok\')">')
    out.write('</TD>')
    out.write('<TD style="text-align: left; vertical-align: middle;">')
    out.write(status_asSPAN('OK'))
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    out.write('</FORM>\n')
    return


##############################################################################
### Node-specific reports
##############################################################################

def write_node_report(node, allpkgs):
    print "BBS> [write_node_report] Node %s: BEGIN..." % node.id
    node_index_file = '%s-index.html' % node.id
    out = open(node_index_file, 'w')
    title = "%s: Build/check report for %s" % (BBSreportutils.get_build_label(), node.id)
    write_top_asHTML(out, title, 'report.css', 'report.js')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    out.write('<BR>\n')
    write_motd_asTABLE(out)
    write_glyph_table(out)
    write_propagation_glyph_table(out)
    write_select_status_table(out)
    out.write('<HR>\n')
    write_compactreport_asTABLE(out, node, allpkgs)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    print "BBS> [write_node_report] Node %s: END" % node.id
    return node_index_file

def make_all_NodeReports(allpkgs):
    if len(BBSreportutils.NODES) != 1:
        for node in BBSreportutils.NODES:
            write_node_report(node, allpkgs)
    return


##############################################################################
### Main page (multiple platform report)
##############################################################################

def write_mainpage_asHTML(out, allpkgs):
    if BBScorevars.mode in ["bioc", "biocLite", "data-experiment"]:
        write_BioC_mainpage_head_asHTML(out)
    else: # "cran" mode
        write_CRAN_mainpage_head_asHTML(out)
    out.write('<BR>\n')
    write_node_specs_table(out)
    out.write('<BR>\n')
    write_glyph_table(out)
    write_propagation_glyph_table(out)
    write_select_status_table(out)
    out.write('<HR>\n')
    if len(BBSreportutils.NODES) != 1: # change 2 back to 1!!!! fixme dan dante
        write_mainreport_asTABLE(out, allpkgs)
    else:
        write_compactreport_asTABLE(out, BBSreportutils.NODES[0], allpkgs)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    return

def make_BioC_MainReport(allpkgs):
    print "BBS> [make_BioC_MainReport] BEGIN..."
    out = open('index.html', 'w')
    write_mainpage_asHTML(out, allpkgs)
    out.close()
    print "BBS> [make_BioC_MainReport] END."
    return

def make_CRAN_MainReport(allpkgs):
    print "BBS> [make_CRAN_MainReport] BEGIN..."
    out = open('index.html', 'w')
    write_mainpage_asHTML(out, allpkgs)
    out.close()
    print "BBS> [make_CRAN_MainReport] END."
    return


##############################################################################
### MAIN SECTION
##############################################################################

print "BBS> [stage8] STARTING stage8 at %s..." % time.asctime()

report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
report_path = BBScorevars.getenv('BBS_REPORT_PATH')
css_file = BBScorevars.getenv('BBS_REPORT_CSS', False)
bgimg_file = BBScorevars.getenv('BBS_REPORT_BGIMG', False)
js_file = BBScorevars.getenv('BBS_REPORT_JS', False)

argc = len(sys.argv)
if argc > 1:
    arg1 = sys.argv[1]
else:
    arg1 = ""

no_alphabet_dispatch = arg1 == "no-alphabet-dispatch"

print "BBS> [stage8] remake_dir %s" % report_path
bbs.fileutils.remake_dir(report_path)
print "BBS> [stage8] cd %s/" % report_path
os.chdir(report_path)
print "BBS> [stage8] get %s from %s/" % (BBScorevars.meat_index_file, BBScorevars.Central_rdir.label)
BBScorevars.Central_rdir.Get(BBScorevars.meat_index_file)
print "BBS> [stage8] get %s from %s/" % (BBSreportutils.STATUS_DB_file, BBScorevars.Central_rdir.label)
BBScorevars.Central_rdir.Get(BBSreportutils.STATUS_DB_file)

BBSreportutils.set_NODES(report_nodes)
if len(BBSreportutils.NODES) != 1:
    main_page_title = 'Multiple platform build/check report'
else:
    main_page_title = 'Build/check report'
allpkgs = BBSreportutils.get_pkgs_from_meat_index()
make_STATUS_SUMMARY(allpkgs)
print "BBS> [stage8] cp %s %s/" % (css_file, report_path)
shutil.copy(css_file, report_path)
if bgimg_file:
    print "BBS> [stage8] cp %s %s/" % (bgimg_file, report_path)
    shutil.copy(bgimg_file, report_path)
if js_file:
    print "BBS> [stage8] cp %s %s/" % (js_file, report_path)
    shutil.copy(js_file, report_path)
for color in ["Red", "Green", "Blue"]:
    icon = "%s/images/120px-%s_Light_Icon.svg.png" % (os.getenv("BBS_HOME"), color)
    shutil.copy(icon, report_path)
print "BBS> [stage8] Generating report for nodes: %s" % report_nodes
if arg1 != "skip-leaf-reports":
    make_all_LeafReports(allpkgs)
make_all_NodeReports(allpkgs)
if BBScorevars.mode != "cran":
    make_BioC_MainReport(allpkgs)
else: # "cran" mode
    make_CRAN_MainReport(allpkgs)

print "BBS> [stage8] DONE at %s." % time.asctime()

#from IPython.core.debugger import Tracer;Tracer()()
