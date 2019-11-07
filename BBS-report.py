#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Sep 16, 2019
###

import sys
import os
import time
import shutil
import re
import fnmatch
import string

import bbs.fileutils
import bbs.parse
import bbs.rdir
import bbs.jobs
import bbs.html
import BBScorevars
import BBSvars
import BBSreportutils


class LeafReportReference:
    def __init__(self, pkg, node_hostname, node_id, stage):
        self.pkg = pkg
        self.node_hostname = node_hostname
        self.node_id = node_id
        self.stage = stage

def wopen_leafreport_input_file(pkg, node_id, stage, filename, return_None_on_error=False):
    if pkg:
        filename = "%s.%s-%s" % (pkg, stage, filename)
    rdir = BBScorevars.nodes_rdir.subdir('%s/%s' % (node_id, stage))
    return rdir.WOpen(filename, return_None_on_error=return_None_on_error)

STATUS_SUMMARY = {}

def update_STATUS_SUMMARY(pkg, node_id, stage, status):
    if node_id not in STATUS_SUMMARY:
        STATUS_SUMMARY[node_id] = { 'install':     (0, 0, 0, 0, 0), \
                                    'buildsrc':    (0, 0, 0, 0, 0), \
                                    'checksrc':    (0, 0, 0, 0, 0), \
                                    'buildbin':    (0, 0, 0, 0, 0) }
    x = STATUS_SUMMARY[node_id][stage]
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
    STATUS_SUMMARY[node_id][stage] = (x0, x1, x2, x3, x4)
    return

def make_STATUS_SUMMARY(allpkgs):
    for pkg in allpkgs:
        for node in BBSreportutils.supported_nodes(pkg):

            # INSTALL status
            if BBScorevars.subbuilds != "bioc-longtests":
                stage = 'install'
                status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
                update_STATUS_SUMMARY(pkg, node.id, stage, status)

            # BUILD status
            stage = 'buildsrc'
            status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
            update_STATUS_SUMMARY(pkg, node.id, stage, status)
            skipped_is_OK = status in ["TIMEOUT", "ERROR"]

            # CHECK status
            if BBScorevars.subbuilds != "workflows":
                stage = 'checksrc'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
                update_STATUS_SUMMARY(pkg, node.id, stage, status)

            # BUILD BIN status
            if BBSreportutils.is_doing_buildbin(node):
                stage = 'buildbin'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
                update_STATUS_SUMMARY(pkg, node.id, stage, status)
    return


##############################################################################
### HTMLization
##############################################################################

def writeThinRowSeparator_asTR(out, tr_class=None):
    if tr_class:
        tr_class = ' class="%s"' % tr_class
    else:
        tr_class = '';
    colspan = BBSreportutils.ncol_to_display(BBScorevars.subbuilds) + 3
    out.write('<TR%s><TD COLSPAN="%s" style="height: 4pt; background: inherit;"></TD></TR>\n' % (tr_class, colspan))
    return

def pkgname_to_HTML(pkg):
    if BBScorevars.subbuilds == "cran":
        url = "https://cran.rstudio.com/web/packages/%s/" % pkg
    else:
        bioc_version = BBScorevars.getenv('BBS_BIOC_VERSION', False)
        subbuilds = BBScorevars.subbuilds
        if subbuilds == "data-annotation":
            repo = "data/annotation"
        elif subbuilds == "data-experiment":
            repo = "data/experiment"
        elif subbuilds == "workflows":
            repo = "workflows"
        else:
            repo = "bioc"
        url = "/packages/%s/%s/html/%s.html" % (bioc_version, repo, pkg)
    return '<A href="%s">%s</A>' % (url, pkg)


##############################################################################
### VCS metadata HTMLization
##############################################################################

def keyval_to_HTML(key, val):
    key = key.replace(' ', '&nbsp;')
    val = val.replace(' ', '&nbsp;')
    return '%s:&nbsp;<SPAN class="svn_info">%s</SPAN>' % (key, val)

def write_keyval_asTD(out, key, val):
    html = keyval_to_HTML(key, val)
    out.write('<TD class="svn_info">%s</TD>' % html)
    return

def write_pkg_keyval_asTD(out, pkg, key):
    val = BBSreportutils.get_vcs_meta(pkg, key)
    write_keyval_asTD(out, key, val)
    return

def write_Date_asTD(out, pkg, key, full_line=True):
    val = BBSreportutils.get_vcs_meta(pkg, key)
    if not full_line:
        val = ' '.join(val.split(' ')[0:3])
    write_keyval_asTD(out, key, val)
    return

def write_LastChange_asTD(out, pkg, key, with_Revision=False):
    val = BBSreportutils.get_vcs_meta(pkg, key)
    html = keyval_to_HTML(key, val)
    if with_Revision:
        key2 = 'Revision'
        val2 = BBSreportutils.get_vcs_meta(pkg, key2)
        html2 = keyval_to_HTML(key2, val2)
        html = '%s / %s' % (html, html2)
    out.write('<TD class="svn_info">%s</TD>' % html)
    return

def write_svn_Changelog_asTD(out, url, pkg):
    if pkg != None:
        url = '%s/%s' % (url, pkg)
    out.write('<TD class="svn_info"><A href="%s">Bioconductor Changelog</A></TD>' % url)
    return

def write_svn_info_for_pkg_asTRs(out, pkg, full_info=False):
    if 'BBS_SVNCHANGELOG_URL' in os.environ:
        url = os.environ['BBS_SVNCHANGELOG_URL']
        out.write('<TR>')
        write_svn_Changelog_asTD(out, url, pkg)
        out.write('</TR>\n')
    if full_info:
        out.write('<TR>')
        write_Date_asTD(out, None, 'Snapshot Date', full_info)
        out.write('</TR>\n')
        out.write('<TR>')
        write_pkg_keyval_asTD(out, pkg, 'URL')
        out.write('</TR>\n')
    out.write('<TR>')
    write_LastChange_asTD(out, pkg, 'Last Changed Rev', True)
    out.write('</TR>\n')
    out.write('<TR>')
    write_Date_asTD(out, pkg, 'Last Changed Date', full_info)
    out.write('</TR>\n')
    return

def write_git_log_for_pkg_asTRs(out, pkg, full_info=False):
    ## metadata other than snapshot date exists only for individual pkg repos
    if pkg == None:
        out.write('<TR>')
        write_Date_asTD(out, None, 'Snapshot Date', full_info)
        out.write('</TR>\n')
    else:
        if full_info:
            out.write('<TR>')
            write_Date_asTD(out, None, 'Snapshot Date', full_info)
            out.write('</TR>\n')
            out.write('<TR>')
            write_pkg_keyval_asTD(out, pkg, 'URL')
            out.write('</TR>\n')
            out.write('<TR>')
            write_pkg_keyval_asTD(out, pkg, 'Branch')
            out.write('</TR>\n')
        out.write('<TR>')
        write_LastChange_asTD(out, pkg, 'Last Commit', False)
        out.write('</TR>\n')
        out.write('<TR>')
        write_Date_asTD(out, pkg, 'Last Changed Date', full_info)
        out.write('</TR>\n')
    return

def write_vcs_meta_for_pkg_asTABLE(out, pkg, full_info=False, with_heading=False):
    if BBSvars.MEAT0_type == 1:
        vcs = 'svn'
        heading = 'svn info'
    else:
        vcs = 'git'
        heading = 'git log'
    if with_heading:
        out.write('<P>%s</P>\n' % heading)
    out.write('<TABLE class="svn_info">\n')
    if BBSvars.MEAT0_type == 1:
        write_svn_info_for_pkg_asTRs(out, pkg, full_info)
    else:
        write_git_log_for_pkg_asTRs(out, pkg, full_info)
    out.write('</TABLE>\n')
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

def write_pkg_status_asTD(out, pkg, node, stage, leafreport_ref, style=None):
    #print("  %s %s %s" % (pkg, node.id, stage))
    status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
    if status in ["skipped", "NA"]:
        status_html = status_asSPAN(status)
    else:
        if leafreport_ref != None:
            pkgdir = "."
        else:
            pkgdir = pkg
        leafreport_rURL = BBSreportutils.get_leafreport_rel_url(pkgdir, node.id, stage)
        status_html = '<A href="%s">%s</A>' % (leafreport_rURL, status_asSPAN(status))
        if leafreport_ref != None \
           and pkg == leafreport_ref.pkg \
           and node.id == leafreport_ref.node_id \
           and stage == leafreport_ref.stage:
            status_html = '[%s]' % status_html
    if style == None:
        style = ""
    else:
        style = ' style="%s"' % style
    out.write('<TD class="status %s %s"%s>%s</TD>' % (node.hostname, stage, style, status_html))
    return

def write_stagelabel_asTD(out, stage, extra_style=""):
    out.write('<TD class="stage %s" style="text-align: center%s">' % \
              (stage, extra_style))
    out.write(BBSreportutils.stage_label(stage))
    out.write('</TD>')
    return

def write_pkg_stagelabels_asTDs(out, extra_style=""):
    subbuilds = BBScorevars.subbuilds
    for stage in BBSreportutils.stages_to_display(subbuilds):
        write_stagelabel_asTD(out, stage, extra_style)
    if BBSreportutils.display_propagation_status(subbuilds):
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

def write_pkg_statuses_asTDs(out, pkg, node, leafreport_ref, style=None):
    subbuilds = BBScorevars.subbuilds
    skipped_pkgs = BBSreportutils.get_pkgs_from_skipped_index()
    if BBSreportutils.is_supported(pkg, node):
        for stage in BBSreportutils.stages_to_display(subbuilds):
            if stage == 'buildbin' and not BBSreportutils.is_doing_buildbin(node):
                out.write('<TD class="node %s"></TD>' % node.hostname.replace(".", "_"))
            else:
                write_pkg_status_asTD(out, pkg, node, stage, leafreport_ref, style)
        if BBSreportutils.display_propagation_status(subbuilds):
            write_pkg_propagation_status_asTD(out, pkg, node)
    else:
        if pkg in skipped_pkgs:
            out.write('<TD COLSPAN="%s" class="node %s">' % \
                     (BBSreportutils.ncol_to_display(subbuilds), \
                      node.hostname.replace(".", "_")) )
            msg = 'ERROR'
            out.write('<SPAN style="text-align: center" class=%s>&nbsp;%s&nbsp;</SPAN>' % (msg, msg))
            out.write(' (Bad DESCRIPTION file)</TD>')
        else:
            out.write('<TD COLSPAN="%s" class="node %s"><I>' % \
                     (BBSreportutils.ncol_to_display(subbuilds), \
                      node.hostname.replace(".", "_")) )
            sep = '...'
            NOT_SUPPORTED_string = sep + 1 * ('NOT SUPPORTED' + sep)
            out.write(NOT_SUPPORTED_string.replace(' ', '&nbsp;'))
            out.write('</I></TD>')
    return

def write_abc_dispatcher(out, href="", current_letter=None,
                                       activate_current_letter=False):
    out.write('<TABLE class="abc_dispatcher"><TR>')
    for i in range(65,91):
        letter = chr(i)
        if letter == current_letter and not activate_current_letter:
            out.write('<TD style="background: inherit;">%s</TD>' % letter)
            continue
        html_letter = '<A href="%s#%s">%s</A>' % (href, letter, letter)
        if letter == current_letter:
            html_letter = '<B>[%s]</B>' % html_letter
        out.write('<TD>%s</TD>' % html_letter)
    out.write('</TR></TABLE>')
    return

### Produces 2 full TRs (normally 8 TDs each, only 4 for longtests subbuilds)
def write_pkg_index_as2fullTRs(out, current_letter):
    ## FH: Need the abc class to blend out the alphabetical selection when
    ## "ok" packages are unselected.
    writeThinRowSeparator_asTR(out, "abc")
    out.write('<TR class="abc">')
    out.write('<TD>')
    out.write('<TABLE class="big_letter"><TR><TD>')
    out.write('<A name="%s">%s</A>' % \
              (current_letter, current_letter))
    out.write('</TD></TR></TABLE>')
    out.write('</TD>')
    colspan = BBSreportutils.ncol_to_display(BBScorevars.subbuilds) + 2
    out.write('<TD COLSPAN="%s" style="background: inherit;">' % colspan)
    write_abc_dispatcher(out, "", current_letter)
    out.write('</TD>')
    out.write('</TR>\n')
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
    ## the "timeout", "error" or "warnings". Note that this means that
    ## a package could end up being tagged with the "ok" class even if it
    ## doesn't have any OK in 'statuses' (e.g. if it's unsupported on all
    ## platforms).
    if classes == "":
        classes = " ok"
    return classes

### Produces full TRs (normally 8 TDs each, only 4 for longtests subbuilds)
def write_pkg_allstatuses_asfullTRs(out, pkg, pkg_pos, nb_pkgs, leafreport_ref):
    if leafreport_ref == None and pkg_pos % 2 == 0:
        classes = "even"
    else:
        classes = "odd"
    statuses = BBSreportutils.get_distinct_statuses_from_db(pkg)
    skipped_pkgs = BBSreportutils.get_pkgs_from_skipped_index()
    if pkg in skipped_pkgs:
        classes += ' error'
    else:
        classes += statuses2classes(statuses)
    out.write('<TR class="%s header">' % classes)
    out.write('<TD>Package <B>%d</B>/%d</TD>' % (pkg_pos, nb_pkgs))
    out.write('<TD style="text-align: left">Hostname</TD>')
    out.write('<TD style="text-align: left; width: 290px">OS&nbsp;/&nbsp;Arch</TD>')
    if leafreport_ref == None:
        extra_style = ""
    else:
        extra_style = "; width: 96px"
    write_pkg_stagelabels_asTDs(out, extra_style)
    out.write('</TR>\n')
    nb_nodes = len(BBSreportutils.NODES)
    is_first = True
    for node in BBSreportutils.NODES:
        out.write('<TR class="%s">' % classes)
        if is_first:
            pkgname_html = pkgname_to_HTML(pkg)
            if statuses:
                version = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Version')
                maintainer = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Maintainer')
                status = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'PackageStatus')
            else:
                version = ''
                maintainer = ''
                status = ''
            if status == "Deprecated":
                strike = '<s>'
                strike_close = '</s>'
            else:
                strike = ''
                strike_close = ''
            out.write('<TD ROWSPAN="%d" style="padding-left: 12px; vertical-align: top;">' \
                      % nb_nodes)
            #out.write('<H3>%s</H3>' % pkgname_html)
            #out.write('<H4>%s</H4>' % version)
            #out.write('<B><SPAN style="font-size: larger;">%s</SPAN>&nbsp;%s</B><BR>' % (pkgname_html, version))
            out.write('<B>%s%s%s&nbsp;%s</B>' % (strike, pkgname_html, strike_close, version))
            out.write('<BR>%s' % maintainer)

            if (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
                out.write('<BR>')
                write_vcs_meta_for_pkg_asTABLE(out, pkg, leafreport_ref != None)
            out.write('</TD>')
            is_first = False
        write_node_spec_asTD(out, node, '<I>%s</I>' % node.id, leafreport_ref)
        write_node_spec_asTD(out, node, nodeOSArch_asSPAN(node), leafreport_ref)
        #if leafreport_ref == None:
        #    style = None
        #else:
        #    style = "font-size: smaller"
        write_pkg_statuses_asTDs(out, pkg, node, leafreport_ref)
        out.write('</TR>\n')
    return

def write_summary_TD(out, node, stage):
    stats = STATUS_SUMMARY[node.id][stage]
    html = '<TABLE class="summary"><TR>'
    html += '<TD class="summary %s">%d</TD>' % ("TIMEOUT", stats[0])
    html += '<TD class="summary %s">%d</TD>' % ("ERROR", stats[1])
    if stage == 'checksrc':
        html += '<TD class="summary %s">%d</TD>' % ("WARNINGS", stats[2])
    html += '<TD class="summary %s">%d</TD>' % ("OK", stats[3])
    # Only relevant when "smart STAGE2" is enabled.
    #if stage == 'install':
    #    html += '<TD class="summary %s">%d</TD>' % ("NotNeeded", stats[4])
    html += '</TR></TABLE>'
    #out.write('<TD class="status %s %s">%s</TD>' % (node.hostname.replace(".", "_"), stage, html))
    out.write('<TD>%s</TD>' % html)
    return

### Produces full TRs (normally 8 TDs each, only 7 for the workflow subbuilds,
### and only 4 for the longtests subbuilds)
def write_summary_asfullTRs(out, nb_pkgs, current_node=None):
    out.write('<TR class="summary header">')
    out.write('<TD COLSPAN="2" style="background: inherit;">SUMMARY</TD>')
    out.write('<TD style="text-align: left; width: 290px">OS&nbsp;/&nbsp;Arch</TD>')
    write_pkg_stagelabels_asTDs(out)
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
        subbuilds = BBScorevars.subbuilds
        for stage in BBSreportutils.stages_to_display(subbuilds):
            if stage == 'buildbin' and not BBSreportutils.is_doing_buildbin(node):
                out.write('<TD></TD>')
            else:
                write_summary_TD(out, node, stage)
        if BBSreportutils.display_propagation_status(subbuilds):
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

### Produces a full TR (normally 8 TDs, only 4 for longtests subbuilds)
def write_compactreport_header_asfullTR(out):
    ## Using the abc class here too to blend out the alphabetical selection +
    ## this header when "ok" packages are unselected.
    out.write('<TR class="header abc">')
    out.write('<TD style="width: 50px;"></TD>')
    out.write('<TD style="text-align: left; padding-left: 12px;">Package</TD>')
    out.write('<TD style="text-align: left">Maintainer</TD>')
    write_pkg_stagelabels_asTDs(out)
    out.write('</TR>\n')
    return

### Produces a full TR (normally 8 TDs, only 4 for longtests subbuilds)
def write_compactreport_fullTR(out, pkg, node, pkg_pos, nb_pkgs, leafreport_ref):
    if pkg_pos % 2 == 0 and not leafreport_ref:
        classes = "even"
    else:
        classes = "odd"
    statuses = BBSreportutils.get_distinct_statuses_from_db(pkg, [node])
    skipped_pkgs = BBSreportutils.get_pkgs_from_skipped_index()
    if pkg in skipped_pkgs:
        classes += ' error'
    else:
        classes += statuses2classes(statuses)
    out.write('<TR class="%s">' % classes)
    out.write('<TD class="header" style="text-align: right;"><B>%d</B>/%d</TD>' % (pkg_pos, nb_pkgs))
    out.write('<TD style="text-align: left; padding-left: 12px;">')

    if statuses:
        version = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Version')
        status = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'PackageStatus')
        maintainer = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'Maintainer')
    else:
        version = ''
        status = ''
        maintainer = ''
    if status == "Deprecated":
        strike = "<s>"
        strike_close = "</s>"
    else:
        strike = ""
        strike_close = ""
    out.write('%s<B>%s</B>%s&nbsp;<B>%s</B>' % (strike, pkgname_to_HTML(pkg), strike_close, version))
    out.write('</TD>')
    out.write('<TD style="text-align: left">%s</TD>' % maintainer)
    write_pkg_statuses_asTDs(out, pkg, node, leafreport_ref)
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

def write_HTML_header(out, page_title=None, css_file=None, js_file=None):
    report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(BBScorevars.subbuilds,
                                             report_nodes)
    out.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"')
    out.write(' "http://www.w3.org/TR/html4/loose.dtd">\n')
    out.write('<HTML>\n')
    out.write('<HEAD>\n')
    out.write('<script language="javascript">\n')
    out.write('if (!/\.html$|\/$|#/.test(window.location.href))\n')
    out.write('  window.location.href = window.location.href + "/";\n')
    out.write('</script>\n')
    out.write('<META http-equiv="Content-Type" content="text/html; charset=UTF-8">\n')
    if page_title:
        title += " - " + page_title
    out.write('<TITLE>%s</TITLE>\n' % title)
    if css_file:
        out.write('<LINK rel="stylesheet" href="%s" type="text/css">\n' % css_file)
    if js_file:
        out.write('<SCRIPT type="text/javascript" src="%s"></SCRIPT>\n' % js_file)
    out.write('</HEAD>\n')
    return

def write_goback_asHTML(out, href, current_letter=None):
    report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(BBScorevars.subbuilds,
                                             report_nodes)
    out.write('<TABLE class="grid_layout"')
    out.write(' style="width: 100%; background: #BBB;"><TR>')
    out.write('<TD style="text-align: left; padding-left: 5px; vertical-align: middle;">')
    out.write('<I><A href="%s">Back to <B>%s</B></A></I>' % (href, title))
    out.write('</TD>')
    if not no_alphabet_dispatch and current_letter != None:
        out.write('<TD>')
        write_abc_dispatcher(out, href, current_letter, True)
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

def make_MultiPlatformPkgIndexPage(leafreport_ref, allpkgs):
    report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(BBScorevars.subbuilds,
                                             report_nodes)

    pkg = leafreport_ref.pkg
    page_title = 'Results for %s' % pkg
    out_rURL = os.path.join(pkg, 'index.html')
    out = open(out_rURL, 'w')

    write_HTML_header(out, page_title, '../report.css')
    out.write('<BODY>\n')
    current_letter = pkg[0:1].upper()
    write_goback_asHTML(out, "../index.html", current_letter)
    out.write('<BR>\n')
    out.write('<H1>%s</H1>\n' % title)
    out.write('<H2>%s</H2>\n' % page_title)
    out.write('<P class="time_stamp">\n')
    date = bbs.jobs.currentDateString()
    out.write('This page was generated on %s.\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)

    write_mainreport_asTABLE(out, allpkgs, leafreport_ref)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

def write_Summary_asHTML(out, node_hostname, pkg, node_id, stage):
    out.write('<HR>\n<H3>Summary</H3>\n')
    dcf = wopen_leafreport_input_file(pkg, node_id, stage, "summary.dcf")
    out.write('<DIV class="%s hscrollable">\n' % \
              node_hostname.replace(".", "_"))
    out.write('<TABLE>\n')
    while True:
        field_val = bbs.parse.getNextDcfFieldVal(dcf, True)
        if not field_val:
            break
        if field_val[0] == 'Status':
            field_val = (field_val[0], status_asSPAN(field_val[1]))
        out.write('<TR><TD><B>%s</B>: %s</TD></TR>\n' % field_val)
    out.write('</TABLE>\n')
    out.write('</DIV>\n')
    dcf.close()
    return

def write_filepath_asHTML(out, Rcheck_dir, filepath):
    span_class = "filename"
    if fnmatch.fnmatch(filepath, "*.fail"):
        span_class += " fail"
    out.write('<P><SPAN class="%s">%s</SPAN></P>\n' % \
              (span_class, os.path.join(Rcheck_dir, filepath)))
    return

### Write content of file 'f' to report.
def write_file_asHTML(out, f, node_hostname, pattern=None):
    encoding = BBScorevars.getNodeSpec(node_hostname, 'encoding')
    pattern_detected = False
    if pattern != None:
        regex = re.compile(pattern)
    out.write('<DIV class="%s hscrollable">\n' % \
              node_hostname.replace(".", "_"))
    out.write('<PRE style="padding: 3px;">\n')
    i = 0
    for line in f:
        i = i + 1
        if i > 99999:
            out.write('... [output truncated]\n')
            break
        line = bbs.parse.bytes2str(line)
        if pattern != None and regex.match(line):
            pattern_detected = True
        #try:
        #    html_line = bbs.html.encodeHTMLentities(line, encoding) # untrusted
        #except:
        #    html_line = line
        html_line = bbs.html.encodeHTMLentities(line, encoding) # untrusted
        try:
            out.write(html_line)
        except UnicodeEncodeError:
            out.write(html_line.encode(encoding))
    out.write('</PRE>\n')
    out.write('</DIV>')
    return pattern_detected

def write_Command_output_asHTML(out, node_hostname, pkg, node_id, stage):
    if stage == "checksrc" and BBScorevars.subbuilds == "bioc-longtests":
        out.write('<HR>\n<H3>&apos;R CMD check&apos; output</H3>\n')
    else:
        out.write('<HR>\n<H3>Command output</H3>\n')
    try:
        f = wopen_leafreport_input_file(pkg, node_id, stage, "out.txt")
    except bbs.rdir.WOpenError:
        out.write('<P class="noresult"><SPAN>')
        out.write('Due to an anomaly in the Build System, this output ')
        out.write('is not available. We apologize for the inconvenience.')
        out.write('</SPAN></P>\n')
    else:
        write_file_asHTML(out, f, node_hostname)
        f.close()
    return

def write_Installation_output_asHTML(out, node_hostname, pkg, node_id):
    out.write('<HR>\n<H3>Installation output</H3>\n')
    Rcheck_dir = pkg + ".Rcheck"
    Rcheck_path = os.path.join(BBScorevars.central_rdir_path, "nodes",
                               node_id, "checksrc", Rcheck_dir)
    if not os.path.exists(Rcheck_path):
        out.write('<P class="noresult"><SPAN>')
        out.write('Due to an anomaly in the Build System, this output ')
        out.write('is not available. We apologize for the inconvenience.')
        out.write('</SPAN></P>\n')
        return
    filename = '00install.out'
    filepath = os.path.join(Rcheck_dir, filename)
    f = wopen_leafreport_input_file(None, node_id, "checksrc", filepath,
                                    return_None_on_error=True)
    if f != None:
        write_filepath_asHTML(out, Rcheck_dir, filename)
        write_file_asHTML(out, f, node_hostname)
        f.close()
    return

def build_test2filename_dict(dirpath, dups):
    p = re.compile('(.*)\.Rout.*')
    test2filename = {}
    for filename in os.listdir(dirpath):
        m = p.match(filename)
        if m != None:
            testname = m.group(1)
            if testname in test2filename:
                dups.append(filename)
            else:
                test2filename[testname] = filename
    return test2filename

def write_Tests_outputs_in_2TD_TRs(out, node_hostname, Rcheck_dir,
                                   tests_dir1, tests_dir2):
    unpaired1 = []
    test2filename1 = build_test2filename_dict(tests_dir1, unpaired1)
    unpaired2 = []
    test2filename2 = build_test2filename_dict(tests_dir2, unpaired2)
    testnames1 = sorted(test2filename1.keys(), key=str.lower)
    ## Paired tests.
    for testname in testnames1:
        if testname in test2filename2:
            out.write('<TR>\n')
            filepath = os.path.join(tests_dir1, test2filename1[testname])
            out.write('<TD>\n')
            write_filepath_asHTML(out, Rcheck_dir, filepath)
            # Encoding is unknown so open in binary mode.
            # write_file_asHTML() will try to decode with bbs.parse.bytes2str()
            f = open(filepath, 'rb')
            write_file_asHTML(out, f, node_hostname)
            f.close()
            out.write('</TD>\n')
            filepath = os.path.join(tests_dir2, test2filename2[testname])
            out.write('<TD style="padding-left: 18px;">\n')
            write_filepath_asHTML(out, Rcheck_dir, filepath)
            # Encoding is unknown so open in binary mode.
            # write_file_asHTML() will try to decode with bbs.parse.bytes2str()
            f = open(filepath, 'rb')
            write_file_asHTML(out, f, node_hostname)
            f.close()
            out.write('</TD>\n')
            out.write('</TR>\n')
            del test2filename1[testname]
            del test2filename2[testname]
    ## Test output files in 'tests_dir1' that didn't get paired.
    unpaired1 += test2filename1.values()
    unpaired1.sort(key=str.lower)
    for filename in unpaired1:
        out.write('<TR>\n')
        filepath = os.path.join(tests_dir1, filename)
        out.write('<TD>\n')
        write_filepath_asHTML(out, Rcheck_dir, filepath)
        # Encoding is unknown so open in binary mode.
        # write_file_asHTML() will try to decode with bbs.parse.bytes2str()
        f = open(filepath, 'rb')
        write_file_asHTML(out, f, node_hostname)
        f.close()
        out.write('</TD>\n')
        out.write('<TD style="padding-left: 18px;"></TD>\n')
        out.write('</TR>\n')
    ## Test output files in 'tests_dir2' that didn't get paired.
    unpaired2 += test2filename2.values()
    unpaired2.sort(key=str.lower)
    for filename in unpaired2:
        out.write('<TR>\n')
        out.write('<TD></TD>\n')
        filepath = os.path.join(tests_dir2, filename)
        out.write('<TD style="padding-left: 18px;">\n')
        write_filepath_asHTML(out, Rcheck_dir, filepath)
        # Encoding is unknown so open in binary mode.
        # write_file_asHTML() will try to decode with bbs.parse.bytes2str()
        f = open(filepath, 'rb')
        write_file_asHTML(out, f, node_hostname)
        f.close()
        out.write('</TD>\n')
        out.write('</TR>\n')
    return

def write_Tests_outputs_from_dir(out, node_hostname, Rcheck_dir, tests_dir):
    p = re.compile('(.*)\.Rout.*')
    filenames = []
    for filename in os.listdir(tests_dir):
        m = p.match(filename)
        if m != None:
             filenames.append(filename)
    filenames.sort(key=str.lower)
    for filename in filenames:
        filepath = os.path.join(tests_dir, filename)
        write_filepath_asHTML(out, Rcheck_dir, filepath)
        # Encoding is unknown so open in binary mode.
        # write_file_asHTML() will try to decode with bbs.parse.bytes2str()
        f = open(filepath, 'rb')
        write_file_asHTML(out, f, node_hostname)
        f.close()
    return

def write_Tests_output_asHTML(out, node_hostname, pkg, node_id):
    out.write('<HR>\n<H3>Tests output</H3>\n')
    Rcheck_dir = pkg + ".Rcheck"
    Rcheck_path = os.path.join(BBScorevars.central_rdir_path, "nodes",
                               node_id, "checksrc", Rcheck_dir)
    if not os.path.exists(Rcheck_path):
        out.write('<P class="noresult"><SPAN>')
        out.write('Due to an anomaly in the Build System, this output ')
        out.write('is not available. We apologize for the inconvenience.')
        out.write('</SPAN></P>\n')
        return
    old_cwd = os.getcwd()
    os.chdir(Rcheck_path)
    tests_dirs = []
    for tests_dir in os.listdir("."):
        if os.path.isdir(tests_dir) and \
           fnmatch.fnmatch(tests_dir, "tests*"):
            tests_dirs.append(tests_dir)
    if len(tests_dirs) == 2 and \
       'tests_i386' in tests_dirs and 'tests_x64' in tests_dirs:
        out.write('<TABLE class="grid_layout">\n')
        write_Tests_outputs_in_2TD_TRs(out, node_hostname, Rcheck_dir,
                                       'tests_i386', 'tests_x64')
        out.write('</TABLE>\n')
    else:
        for tests_dir in tests_dirs:
            write_Tests_outputs_from_dir(out, node_hostname, Rcheck_dir,
                                         tests_dir)
    os.chdir(old_cwd)
    return

def write_Example_timings_from_file(out, node_hostname, Rcheck_dir, filepath):
    f = open(filepath, 'rb')
    write_filepath_asHTML(out, Rcheck_dir, filepath)
    out.write('<DIV class="%s hscrollable">\n' % \
              node_hostname.replace(".", "_"))
    out.write('<TABLE>\n')
    for line in f:
        line = bbs.parse.bytes2str(line)
        out.write('<TR><TD>')
        out.write(line.replace('\t', '</TD><TD style="text-align: right;">'))
        out.write('</TD><TR>\n')
    out.write('</TABLE>\n')
    out.write('</DIV>')
    f.close()
    return

def write_Example_timings_asHTML(out, node_hostname, pkg, node_id):
    out.write('<HR>\n<H3>Example timings</H3>\n')
    Rcheck_dir = pkg + ".Rcheck"
    Rcheck_path = os.path.join(BBScorevars.central_rdir_path, "nodes",
                               node_id, "checksrc", Rcheck_dir)
    if not os.path.exists(Rcheck_path):
        out.write('<P class="noresult"><SPAN>')
        out.write('Due to an anomaly in the Build System, the timings ')
        out.write('are not available. We apologize for the inconvenience.')
        out.write('</SPAN></P>\n')
        return
    old_cwd = os.getcwd()
    os.chdir(Rcheck_path)
    examples_dirs = []
    for examples_dir in os.listdir("."):
        if os.path.isdir(examples_dir) and \
           fnmatch.fnmatch(examples_dir, "examples*"):
            examples_dirs.append(examples_dir)
    if len(examples_dirs) == 2 and \
       'examples_i386' in examples_dirs and 'examples_x64' in examples_dirs:
        out.write('<TABLE class="grid_layout"><TR>\n')
        out.write('<TD>\n')
        filepath = 'examples_i386/%s-Ex.timings' % pkg
        if os.path.isfile(filepath):
            write_Example_timings_from_file(out, node_hostname, Rcheck_dir,
                                            filepath)
        out.write('</TD>\n')
        out.write('<TD style="padding-left: 18px;">\n')
        filepath = 'examples_x64/%s-Ex.timings' % pkg
        if os.path.isfile(filepath):
            write_Example_timings_from_file(out, node_hostname, Rcheck_dir,
                                            filepath)
        out.write('</TD>\n')
        out.write('</TR></TABLE>\n')
    else:
        filepath = '%s-Ex.timings' % pkg
        if os.path.isfile(filepath):
            write_Example_timings_from_file(out, node_hostname, Rcheck_dir,
                                            filepath)
    os.chdir(old_cwd)
    return

def write_leaf_outputs_asHTML(out, node_hostname, pkg, node_id, stage):
    if stage != "checksrc":
        write_Command_output_asHTML(out, node_hostname, pkg, node_id, stage)
        return
    if BBScorevars.subbuilds == "bioc-longtests":
        write_Tests_output_asHTML(out, node_hostname, pkg, node_id)
    write_Command_output_asHTML(out, node_hostname, pkg, node_id, stage)
    write_Installation_output_asHTML(out, node_hostname, pkg, node_id)
    if BBScorevars.subbuilds != "bioc-longtests":
        write_Tests_output_asHTML(out, node_hostname, pkg, node_id)
        write_Example_timings_asHTML(out, node_hostname, pkg, node_id)
    return

def make_LeafReport(leafreport_ref, allpkgs):
    pkg = leafreport_ref.pkg
    node_hostname = leafreport_ref.node_hostname
    node_id = leafreport_ref.node_id
    stage = leafreport_ref.stage
    page_title = '%s report for %s on %s' % (BBSreportutils.stage_label(stage), pkg, node_id)
    out_rURL = BBSreportutils.get_leafreport_rel_path(pkg, node_id, stage)
    out = open(out_rURL, 'w')

    write_HTML_header(out, page_title, '../report.css')
    out.write('<BODY>\n')
    current_letter = pkg[0:1].upper()
    write_goback_asHTML(out, "../index.html", current_letter)
    out.write('<BR>\n')
    out.write('<H2>%s</H2>\n' % page_title)
    out.write('<P class="time_stamp">\n')
    date = bbs.jobs.currentDateString()
    out.write('This page was generated on %s.\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)

    write_mainreport_asTABLE(out, allpkgs, leafreport_ref)
    #if len(BBSreportutils.NODES) != 1:
    #    write_mainreport_asTABLE(out, allpkgs, leafreport_ref)
    #else:
    #    write_compactreport_asTABLE(out, BBSreportutils.NODES[0], allpkgs, leafreport_ref)

    status = BBSreportutils.get_status_from_db(pkg, node_id, stage)
    if stage == "install" and status == "NotNeeded":
        out.write('<HR>\n')
        out.write('<DIV class="%s">\n' % node_hostname.replace(".", "_"))
        out.write('REASON FOR NOT INSTALLING: no other package that will ')
        out.write('be built and checked on this platform needs %s' % pkg)
        out.write('</DIV>\n')
    else:
        write_Summary_asHTML(out, node_hostname, pkg, node_id, stage)
        write_leaf_outputs_asHTML(out, node_hostname, pkg, node_id, stage)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

def make_node_LeafReports(allpkgs, node):
    print("BBS> [make_node_LeafReports] Node %s: BEGIN ..." % node.id)
    sys.stdout.flush()
    for pkg in BBSreportutils.supported_pkgs(node):

        # INSTALL leaf-report
        if BBScorevars.subbuilds != "bioc-longtests":
            stage = "install"
            status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
            if status != "skipped":
                leafreport_ref = LeafReportReference(pkg,
                                                     node.hostname, node.id,
                                                     stage)
                make_LeafReport(leafreport_ref, allpkgs)

        # BUILD leaf-report
        stage = "buildsrc"
        status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
        if not status in ["skipped", "NA"]:
            leafreport_ref = LeafReportReference(pkg,
                                                 node.hostname, node.id,
                                                 stage)
            make_LeafReport(leafreport_ref, allpkgs)

        # CHECK leaf-report
        if BBScorevars.subbuilds != "workflows":
            stage = 'checksrc'
            status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
            if not status in ["skipped", "NA"]:
                leafreport_ref = LeafReportReference(pkg,
                                                     node.hostname, node.id,
                                                     stage)
                make_LeafReport(leafreport_ref, allpkgs)

        # BUILD BIN leaf-report
        if BBSreportutils.is_doing_buildbin(node):
            stage = "buildbin"
            status = BBSreportutils.get_status_from_db(pkg, node.id, stage)
            if not status in ["skipped", "NA"]:
                leafreport_ref = LeafReportReference(pkg,
                                                     node.hostname, node.id,
                                                     stage)
                make_LeafReport(leafreport_ref, allpkgs)

    print("BBS> [make_node_LeafReports] Node %s: END." % node.id)
    sys.stdout.flush()
    return

def make_all_LeafReports(allpkgs):
    print("BBS> [make_all_LeafReports] Current working dir '%s'" % os.getcwd())
    print("BBS> [make_all_LeafReports] Creating report package subfolders " + \
          "and populating them with the index.html files ...", end=" ")
    sys.stdout.flush()
    for pkg in allpkgs:
        try:
            os.mkdir(pkg)
        except:
            print("mkdir failed in make_all_LeaveReports '%s'" % pkg)
            continue
        leafreport_ref = LeafReportReference(pkg, None, None, None)
        make_MultiPlatformPkgIndexPage(leafreport_ref, allpkgs)
    print("DONE")
    sys.stdout.flush()
    for node in BBSreportutils.NODES:
        make_node_LeafReports(allpkgs, node)
    return


##############################################################################
### Main page: HTML stuff above main table
##############################################################################

def write_BioC_mainpage_top_asHTML(out):
    report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(BBScorevars.subbuilds,
                                             report_nodes)
    write_HTML_header(out, None, 'report.css', 'report.js')
    ## FH: Initialize the checkboxes when page is (re)loaded
    out.write('<BODY onLoad="initialize();">\n')
    out.write('<H1>%s</H1>\n' % title)
    out.write('<P class="time_stamp">\n')
    date = bbs.jobs.currentDateString()
    out.write('This page was generated on %s.\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)
    if (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
        out.write('<DIV class="svn_info">\n')
        write_vcs_meta_for_pkg_asTABLE(out, None, True, True)
        out.write('</DIV>\n')
    return

def write_CRAN_mainpage_top_asHTML(out):
    report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(BBScorevars.subbuilds,
                                             report_nodes)
    write_HTML_header(out, None, 'report.css', 'report.js')
    out.write('<BODY>\n')
    out.write('<H1>%s</H1>\n' % title)
    out.write('<P class="time_stamp">\n')
    date = bbs.jobs.currentDateString()
    out.write('This page was generated on %s.\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)
    return

def read_Rversion(Node_rdir):
    filename = 'NodeInfo/R-version.txt'
    f = Node_rdir.WOpen(filename)
    Rversion = bbs.parse.bytes2str(f.readline())
    f.close()
    Rversion = Rversion.replace('R version ', '')
    Rversion_html = Rversion.replace(' ', '&nbsp;')
    return Rversion_html

def get_Rconfig_value_from_file(Node_rdir, var):
    filename = 'NodeInfo/R-config.txt'
    dcf = Node_rdir.WOpen(filename)
    val = bbs.parse.getNextDcfVal(dcf, var, True)
    dcf.close()
    if val == None:
        filename = '%s/%s' % (Node_rdir.label, filename)
        raise bbs.parse.DcfFieldNotFoundError(filename, var)
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
    filename = 'NodeInfo/%s-version.txt' % var
    f = Node_rdir.WOpen(filename, return_None_on_error=True)
    if f == None:
        return
    cmd = get_Rconfig_value_from_file(Node_rdir, var)
    syscmd = '%s --version' % cmd
    out.write('<P><B>Compiler version</B> (\'%s\' output):</P>\n' % syscmd)
    out.write('<PRE style="margin-left: 12px;">\n')
    for line in f:
        out.write(bbs.parse.bytes2str(line))
    f.close()
    out.write('</PRE>\n')
    return

def make_NodeInfo_page(Node_rdir, node):
    page_title = 'More about %s' % node.id
    NodeInfo_page_path = '%s-NodeInfo.html' % node.id
    out = open(NodeInfo_page_path, 'w')

    write_HTML_header(out, page_title, 'report.css')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    out.write('<BR>\n')
    out.write('<H1>%s</H1>\n' % page_title)

    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    out.write('<TABLE>\n')
    out.write('<TR><TD><B>Hostname:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.hostname)
    out.write('<TR><TD><B>OS:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.os_html)
    out.write('<TR><TD><B>Arch:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.arch)
    out.write('<TR><TD><B>Platform:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.platform)
    out.write('<TR><TD><B>R&nbsp;version:&nbsp;</B></TD><TD>%s</TD></TR>\n' % read_Rversion(Node_rdir))
    out.write('</TABLE>\n')
    out.write('</DIV>\n')

    out.write('<HR>\n')

    out.write('<H2>C compiler</H2>\n')
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    C_vars = ['CC', 'CFLAGS', 'CPICFLAGS', 'CPP']
    write_Rconfig_table_from_file(out, Node_rdir, C_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CC')
    out.write('</DIV>\n')

    out.write('<HR>\n')

    out.write('<H2>C++ compiler</H2>\n')
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    Cplusplus_vars = ['CXX', 'CXXFLAGS', 'CXXPICFLAGS', 'CXXCPP']
    write_Rconfig_table_from_file(out, Node_rdir, Cplusplus_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CXX')
    out.write('</DIV>\n')

    out.write('<HR>\n')

    #out.write('<H2>C++98 compiler</H2>\n')
    #out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    #Cplusplus98_vars = ['CXX98', 'CXX98FLAGS', 'CXX98PICFLAGS', 'CXX98STD']
    #write_Rconfig_table_from_file(out, Node_rdir, Cplusplus98_vars)
    #write_SysCommandVersion_from_file(out, Node_rdir, 'CXX98')
    #out.write('</DIV>\n')
    #
    #out.write('<HR>\n')

    out.write('<H2>C++11 compiler</H2>\n')
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    Cplusplus11_vars = ['CXX11', 'CXX11FLAGS', 'CXX11PICFLAGS', 'CXX11STD']
    write_Rconfig_table_from_file(out, Node_rdir, Cplusplus11_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CXX11')
    out.write('</DIV>\n')

    out.write('<HR>\n')

    out.write('<H2>C++14 compiler</H2>\n')
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    Cplusplus14_vars = ['CXX14', 'CXX14FLAGS', 'CXX14PICFLAGS', 'CXX14STD']
    write_Rconfig_table_from_file(out, Node_rdir, Cplusplus14_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CXX14')
    out.write('</DIV>\n')

    out.write('<HR>\n')

    #out.write('<H2>Fortran 77 compiler</H2>\n')
    #out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    #Fortran77_vars = ['F77', 'FFLAGS', 'FLIBS', 'FPICFLAGS']
    #write_Rconfig_table_from_file(out, Node_rdir, Fortran77_vars)
    #write_SysCommandVersion_from_file(out, Node_rdir, 'F77')
    #out.write('</DIV>\n')
    #
    #out.write('<HR>\n')

    #out.write('<H2>Fortran 9x compiler</H2>\n')
    #out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    #Fortran9x_vars = ['FC', 'FCFLAGS', 'FCPICFLAGS']
    #write_Rconfig_table_from_file(out, Node_rdir, Fortran9x_vars)
    #write_SysCommandVersion_from_file(out, Node_rdir, 'FC')
    #out.write('</DIV>\n')
    #
    #out.write('<HR>\n')

    out.write('<P>More information might be added in the future...</P>\n')

    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return NodeInfo_page_path

### Make local copy (and rename) R-instpkgs.txt file.
### Returns the 2-string tuple containing the filename of the generated page
### and the number of installed pkgs.
def make_Rinstpkgs_page(Node_rdir, node):
    page_title = 'R packages installed on %s' % node.id
    Rinstpkgs_page = '%s-R-instpkgs.html' % node.id
    out = open(Rinstpkgs_page, 'w')

    write_HTML_header(out, page_title, 'report.css')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    out.write('<BR>\n')
    out.write('<H1>%s</H1>\n' % page_title)
    out.write('<P class="time_stamp">\n')
    date = bbs.jobs.currentDateString()
    out.write('This page was generated on %s.\n' % date)
    out.write('</P>\n')

    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    filename = 'NodeInfo/R-instpkgs.txt'
    out.write('<PRE>\n')
    f = Node_rdir.WOpen(filename)
    nline = 0
    for line in f:
        out.write(bbs.parse.bytes2str(line))
        nline += 1
    f.close()
    out.write('</PRE>\n')
    out.write('</DIV></BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return (Rinstpkgs_page, str(nline-1))

def write_node_specs_table(out):
    out.write('<TABLE class="node_specs">\n')
    out.write('<TR>')
    out.write('<TH>Hostname</TH>')
    out.write('<TH>OS</TH>')
    out.write('<TH>Arch&nbsp;(*)</TH>')
    out.write('<TH>Platform&nbsp;label&nbsp;(**)</TH>')
    out.write('<TH>R&nbsp;version</TH>')
    out.write('<TH style="text-align: right;">Installed&nbsp;pkgs</TH>')
    out.write('</TR>\n')
    nodes_rdir = BBScorevars.nodes_rdir
    for node in BBSreportutils.NODES:
        Node_rdir = nodes_rdir.subdir(node.id)
        NodeInfo_page_path = make_NodeInfo_page(Node_rdir, node)
        Rversion_html = read_Rversion(Node_rdir)
        Rinstpkgs_strings = make_Rinstpkgs_page(Node_rdir, node)
        out.write('<TR class="%s">' % node.hostname.replace(".", "_"))
        out.write('<TD><B><A href="%s"><I>%s</I></A></B></TD>' % (NodeInfo_page_path, node.id))
        out.write('<TD>%s</TD>' % node.os_html)
        out.write('<TD>%s</TD>' % node.arch)
        out.write('<TD>%s</TD>' % node.platform)
        out.write('<TD class="spec">%s</TD>' % Rversion_html)
        out.write('<TD class="spec" style="text-align: right;">')
        out.write('<A href="%s">%s</A>' % Rinstpkgs_strings)
        out.write('</TD>')
        out.write('</TR>\n')
    out.write('<TR>')
    out.write('<TD COLSPAN="6" style="font-size: smaller;">')
    out.write('<I>Click on any hostname to see more info about the system (e.g. compilers)')
    out.write(' &nbsp;&nbsp;&nbsp;&nbsp; ')
    out.write('(*) as reported by \'uname -p\', except on Windows and Mac OS X')
    out.write(' &nbsp;&nbsp;&nbsp;&nbsp; ')
    out.write('(**) as reported by \'gcc -v\'</I>')
    out.write('</TD>')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    return

### FH: Create checkboxes to select display types
def write_glyph_table(out):
    def write_checkbox(checkbox_id):
        out.write('<INPUT style="margin: 0px;" type="checkbox" ')
        out.write('checked id="%s" onClick="toggle(\'%s\')">' % \
                  (checkbox_id, checkbox_id))
        return

    def write_glyph(id, msg, checkbox = False, first = False):
        style = ""
        if first:
           style += " width: 75px;"
        out.write('<TR>\n')
        out.write('<TD style="text-align: right;%s">%s</TD>\n' % \
                  (style, status_asSPAN(id)))
        if checkbox:
            out.write('<TD>')
            out.write(msg)
            out.write('</TD>\n')
            out.write('<TD style="text-align: right; vertical-align: middle;">')
            write_checkbox(id.lower())
        else:
            out.write('<TD COLSPAN="2">')
            out.write(msg)
        out.write('</TD>\n')
        if first:
            out.write('<TD ROWSPAN="5" style="width: 85px; text-align: left; font-style: italic;">\n')
            out.write('Use the check boxes to show only packages with the selected status types.')
            out.write('</TD>\n')
        out.write('</TR>\n')
        return

    subbuilds = BBScorevars.subbuilds

    out.write('<FORM action="">\n')
    out.write('<TABLE style="width: 670px; border-spacing: 1px; border: solid black 1px;">\n')

    out.write('<TR>\n')
    out.write('<TD COLSPAN="4" style="font-style: italic; border-bottom: solid black 1px;">')
    out.write('<B>Package status is indicated by one of the following glyphs</B>')
    out.write('</TD>\n')
    out.write('</TR>\n')

    ## "TIMEOUT" glyph
    if subbuilds == "bioc-longtests":
        msg = '<I>CHECK</I>'
    elif subbuilds == "workflows":
        msg = '<I>INSTALL</I> or <I>BUILD</I>'
    else:
        msg = '<I>INSTALL</I>, <I>BUILD</I>, <I>CHECK</I> or <I>BUILD BIN</I>'
    timeout = int(BBScorevars.r_cmd_timeout / 60.0)
    msg += ' of package took more than %d minutes' % timeout
    write_glyph("TIMEOUT", msg, True, True)

    ## "ERROR" glyph
    msg = 'Bad DESCRIPTION file or '
    if subbuilds == "bioc-longtests":
        msg += '<I>CHECK</I> of package produced errors'
    elif subbuilds == "workflows":
        msg += '<I>INSTALL</I> or <I>BUILD</I> of package failed'
    else:
        msg += '<I>INSTALL</I>, <I>BUILD</I> or <I>BUILD BIN</I> of package failed,'
        msg += ' or <I>CHECK</I> produced errors'
    write_glyph("ERROR", msg, True)

    ## "WARNINGS" glyph
    if subbuilds != "workflows":
        msg = '<I>CHECK</I> of package produced warnings'
        write_glyph("WARNINGS", msg, True)

    ## "OK" glyph
    if subbuilds == "bioc-longtests":
        msg = '<I>CHECK</I>'
    elif subbuilds == "workflows":
        msg = '<I>INSTALL</I> or <I>BUILD</I>'
    else:
        msg = '<I>INSTALL</I>, <I>BUILD</I>, <I>CHECK</I> or <I>BUILD BIN</I>'
    msg += ' of package was OK'
    write_glyph("OK", msg, True)

    ## "NotNeeded" glyph (only used when "smart STAGE2" is enabled i.e. when
    ## STAGE2 skips installation of target packages not needed by another
    ## target package for build or check).
    #if subbuilds != "workflows" and subbuilds != "bioc-longtests":
    #    msg = '<I>INSTALL</I> of package was not needed (click on glyph to see why)'
    #    write_glyph("NotNeeded", msg)

    ## "skipped" glyph
    if subbuilds != "bioc-longtests":
        msg = '<I>CHECK</I> or <I>BUILD BIN</I>'
        msg += ' of package was skipped because the <I>BUILD</I> step failed\n'
        write_glyph("skipped", msg)

    ## "NA" glyph
    if subbuilds == "bioc-longtests":
        msg = '<I>CHECK</I>'
    elif subbuilds == "workflows":
        msg = '<I>BUILD</I>'
    else:
        msg = '<I>BUILD</I>, <I>CHECK</I> or <I>BUILD BIN</I>'
    msg += ' result is not available because of an anomaly in the Build System\n'
    write_glyph("NA", msg)

    out.write('<TR>\n')
    out.write('<TD COLSPAN="4" style="font-style: italic; border-top: solid black 1px;">')
    out.write('Click on any glyph in the report below')
    out.write(' to access the detailed results.')
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    out.write('</FORM>\n')
    return

def write_propagation_LED_table(out):
    out.write('<TABLE style="width: 380px; border-spacing: 1px; border: solid black 1px;">\n')
    out.write('<TR>\n')
    out.write('<TD COLSPAN="2" style="text-align: left; font-style: italic; border-bottom: solid black 1px;">')
    out.write('<B>Package propagation status')
    out.write(' is indicated by one of the following LEDs</B>')
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD style="vertical-align: top;"><IMG border="0" width="10px" height="10px" alt="YES" src="120px-Green_Light_Icon.svg.png"></TD>\n')
    out.write('<TD>YES: Package was propagated because it didn\'t previously exist or version was bumped</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD style="vertical-align: top;"><IMG border="0" width="10px" height="10px" alt="NO" src="120px-Red_Light_Icon.svg.png"></TD>\n')
    out.write('<TD>NO: Package was not propagated because of a problem (impossible dependencies, or version lower than what is already propagated)</TD>\n')
    out.write('</TR>\n')
    out.write('<TR>\n')
    out.write('<TD style="vertical-align: top;"><IMG border="0" width="10px" height="10px" alt="UNNEEDED" src="120px-Blue_Light_Icon.svg.png"></TD>\n')
    out.write('<TD>UNNEEDED: Package was not propagated because it is already in the repository with this version. A version bump is required in order to propagate it</TD>\n')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    return

def write_glyph_and_propagation_LED_table(out):
    out.write('<DIV style="font-size: smaller;">\n')
    out.write('<TABLE class="grid_layout"><TR>')
    out.write('<TD>\n')
    write_glyph_table(out)
    out.write('</TD>')
    if BBSreportutils.display_propagation_status(BBScorevars.subbuilds):
        out.write('<TD style="padding-left: 6px;">\n')
        write_propagation_LED_table(out)
        out.write('<P>\n')
        out.write('A <s>crossed-out</s> package name indicates the package is')
        out.write(' <a href="https://bioconductor.org/developers/package-end-of-life/">deprecated</a>')
        out.write('</P>\n')
        out.write('</TD>')
    out.write('</TR></TABLE>\n')
    out.write('</DIV>\n')
    return


##############################################################################
### Node-specific reports
##############################################################################

def write_node_report(node, allpkgs):
    print("BBS> [write_node_report] Node %s: BEGIN ..." % node.id)
    sys.stdout.flush()
    node_index_file = '%s-index.html' % node.id
    out = open(node_index_file, 'w')
    page_title = "Results for %s" % node.id

    write_HTML_header(out, page_title, 'report.css', 'report.js')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    out.write('<BR>\n')
    out.write('<H2>%s</H2>\n' % page_title)
    out.write('<P class="time_stamp">\n')
    date = bbs.jobs.currentDateString()
    out.write('This page was generated on %s.\n' % date)
    out.write('</P>\n')
    write_motd_asTABLE(out)

    write_glyph_and_propagation_LED_table(out)
    out.write('<HR>\n')
    write_compactreport_asTABLE(out, node, allpkgs)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    print("BBS> [write_node_report] Node %s: END." % node.id)
    sys.stdout.flush()
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
    if BBScorevars.subbuilds != "cran":
        write_BioC_mainpage_top_asHTML(out)
    else: # "cran" subbuilds
        write_CRAN_mainpage_top_asHTML(out)
    out.write('<BR>\n')
    write_node_specs_table(out)
    out.write('<BR>\n')
    write_glyph_and_propagation_LED_table(out)
    out.write('<HR>\n')
    if len(BBSreportutils.NODES) != 1: # change 2 back to 1!!!! fixme dan dante
        write_mainreport_asTABLE(out, allpkgs)
    else:
        write_compactreport_asTABLE(out, BBSreportutils.NODES[0], allpkgs)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    return

def make_BioC_MainReport(allpkgs):
    print("BBS> [make_BioC_MainReport] BEGIN ...")
    sys.stdout.flush()
    out = open('index.html', 'w')
    write_mainpage_asHTML(out, allpkgs)
    out.close()
    print("BBS> [make_BioC_MainReport] END.")
    sys.stdout.flush()
    return

def make_CRAN_MainReport(allpkgs):
    print("BBS> [make_CRAN_MainReport] BEGIN ...")
    out = open('index.html', 'w')
    write_mainpage_asHTML(out, allpkgs)
    out.close()
    print("BBS> [make_CRAN_MainReport] END.")
    sys.stdout.flush()
    return


##############################################################################
### MAIN SECTION
##############################################################################

print("BBS> [stage8] STARTING stage8 at %s..." % time.asctime())

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

print("BBS> [stage8] remake_dir %s" % report_path)
bbs.fileutils.remake_dir(report_path)
print("BBS> [stage8] cd %s/" % report_path)
os.chdir(report_path)
print("BBS> [stage8] get %s from %s/" % (BBScorevars.meat_index_file, BBScorevars.Central_rdir.label))
BBScorevars.Central_rdir.Get(BBScorevars.meat_index_file)
print("BBS> [stage8] get %s from %s/" % (BBScorevars.skipped_index_file, BBScorevars.Central_rdir.label))
BBScorevars.Central_rdir.Get(BBScorevars.skipped_index_file)
print("BBS> [stage8] get %s from %s/" % (BBSreportutils.STATUS_DB_file, BBScorevars.Central_rdir.label))
BBScorevars.Central_rdir.Get(BBSreportutils.STATUS_DB_file)

BBSreportutils.set_NODES(report_nodes)

meat_pkgs = BBSreportutils.get_pkgs_from_meat_index()
skipped_pkgs = BBSreportutils.get_pkgs_from_skipped_index()
allpkgs = meat_pkgs + skipped_pkgs
allpkgs.sort(key=str.lower)
make_STATUS_SUMMARY(allpkgs)

print("BBS> [stage8] cp %s %s/" % (css_file, report_path))
shutil.copy(css_file, report_path)
if bgimg_file:
    print("BBS> [stage8] cp %s %s/" % (bgimg_file, report_path))
    shutil.copy(bgimg_file, report_path)
if js_file:
    print("BBS> [stage8] cp %s %s/" % (js_file, report_path))
    shutil.copy(js_file, report_path)
for color in ["Red", "Green", "Blue"]:
    icon = "%s/images/120px-%s_Light_Icon.svg.png" % (os.getenv("BBS_HOME"), color)
    shutil.copy(icon, report_path)
print("BBS> [stage8] Will generate HTML report for nodes: %s" % report_nodes)
if arg1 != "skip-leaf-reports":
    make_all_LeafReports(allpkgs)
make_all_NodeReports(allpkgs)
if BBScorevars.subbuilds != "cran":
    make_BioC_MainReport(allpkgs)
else: # "cran" subbuilds
    make_CRAN_MainReport(allpkgs)

print("BBS> [stage8] DONE at %s." % time.asctime())

#from IPython.core.debugger import Tracer;Tracer()()
