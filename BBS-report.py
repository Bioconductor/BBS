#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: June 16, 2021
###

import sys
import os
import time
import shutil
import re
import fnmatch
import string
import html

import bbs.fileutils
import bbs.parse
import bbs.jobs
import bbs.rdir
import BBSutils
import BBSvars
import BBSreportutils


##############################################################################
### write_vcs_meta_for_pkg_as_TABLE()
##############################################################################

def _make_link_with_mouseover(url, content):
    onmouseover = 'add_class_mouseover(this);'
    onmouseout = 'remove_class_mouseover(this);'
    return '<A href="%s" onmouseover="%s" onmouseout="%s">%s</A>' % \
           (url, onmouseover, onmouseout, content)

def _keyval_as_HTML(key, val):
    key = key.replace(' ', '&nbsp;')
    val = val.replace(' ', '&nbsp;')
    return '%s:&nbsp;<SPAN class="svn_info">%s</SPAN>' % (key, val)

def _write_keyval_as_TD(out, key, val):
    html = _keyval_as_HTML(key, val)
    out.write('<TD class="svn_info">%s</TD>' % html)
    return

def _write_pkg_keyval_as_TD(out, pkg, key):
    val = BBSreportutils.get_vcs_meta(pkg, key)
    _write_keyval_as_TD(out, key, val)
    return

def _write_Date_as_TD(out, pkg, key, full_line=True):
    val = BBSreportutils.get_vcs_meta(pkg, key)
    if not full_line:
        val = ' '.join(val.split(' ')[0:3])
    _write_keyval_as_TD(out, key, val)
    return

def _write_LastChange_as_TD(out, pkg, key, with_Revision=False):
    val = BBSreportutils.get_vcs_meta(pkg, key)
    html = _keyval_as_HTML(key, val)
    if with_Revision:
        key2 = 'Revision'
        val2 = BBSreportutils.get_vcs_meta(pkg, key2)
        html2 = _keyval_as_HTML(key2, val2)
        html = '%s / %s' % (html, html2)
    out.write('<TD class="svn_info">%s</TD>' % html)
    return

def _write_svn_info_for_pkg_as_TRs(out, pkg, full_info=False):
    if full_info:
        out.write('<TR>')
        _write_Date_as_TD(out, None, 'Snapshot Date', full_info)
        out.write('</TR>\n')
        out.write('<TR>')
        _write_pkg_keyval_as_TD(out, pkg, 'URL')
        out.write('</TR>\n')
    out.write('<TR>')
    _write_LastChange_as_TD(out, pkg, 'Last Changed Rev', True)
    out.write('</TR>\n')
    out.write('<TR>')
    _write_Date_as_TD(out, pkg, 'Last Changed Date', full_info)
    out.write('</TR>\n')
    return

def _write_git_log_for_pkg_as_TRs(out, pkg, full_info=False):
    ## metadata other than snapshot date exists only for individual pkg repos
    if pkg == None:
        out.write('<TR>')
        key = 'Approx. Package Snapshot Date (git pull)'
        val = BBSreportutils.get_vcs_meta(None, 'Snapshot Date')
        if not full_info:
            val = ' '.join(val.split(' ')[0:3])
        _write_keyval_as_TD(out, key, val)
        out.write('</TR>\n')
    else:
        if full_info:
            out.write('<TR>')
            _write_Date_as_TD(out, None, 'Snapshot Date', full_info)
            out.write('</TR>\n')
            out.write('<TR>')
            _write_pkg_keyval_as_TD(out, pkg, 'git_url')
            out.write('</TR>\n')
            out.write('<TR>')
            _write_pkg_keyval_as_TD(out, pkg, 'git_branch')
            out.write('</TR>\n')
        out.write('<TR>')
        _write_LastChange_as_TD(out, pkg, 'git_last_commit', False)
        out.write('</TR>\n')
        out.write('<TR>')
        _write_Date_as_TD(out, pkg, 'git_last_commit_date', full_info)
        out.write('</TR>\n')
    return

def write_vcs_meta_for_pkg_as_TABLE(out, pkg, full_info=False):
    out.write('<TABLE class="svn_info">\n')
    if BBSvars.MEAT0_type == 1:
        _write_svn_info_for_pkg_as_TRs(out, pkg, full_info)
    else:
        _write_git_log_for_pkg_as_TRs(out, pkg, full_info)
    out.write('</TABLE>\n')
    return


##############################################################################
### write_explain_glyph_table()
##############################################################################

## Produce a SPAN element.
def _status_as_glyph(status):
    html = status
    if status != 'skipped':
        html = '&nbsp;&nbsp;%s&nbsp;&nbsp;' % html
    return '<SPAN class="glyph %s">%s</SPAN>' % (status, html)

## Produce a TD element (table cell).
def _write_glyph_box(out, status, toggleable=False):
    if toggleable:
        toggle_id = '%s_toggle' % status.lower()
        onmouseover = 'add_class_mouseover(this);'
        onmouseout = 'remove_class_mouseover(this);'
        onclick = 'filter_gcards(\'%s\');' % status.lower()
        TD_attrs = ['class="glyph_box toggle"',
                    'id="%s"' % toggle_id,
                    'onmouseover="%s"' % onmouseover,
                    'onmouseout="%s"' % onmouseout,
                    #'onkeypress="%s"' % onclick,
                    'onclick="%s"' % onclick,
                    'style="width: 110px;"']
        checkbox_id = '%s_checkbox' % status.lower()
        checkbox_attrs = 'id="%s" style="margin: 0px; padding: 0px;"' % \
                         checkbox_id
        checkbox_html = '<INPUT type="checkbox" checked %s>' % checkbox_attrs
    else:
        TD_attrs = ['class="glyph_box"']
        checkbox_html = ''
    TD1_style = 'text-align: left; padding-left: 3px; padding-right: 3px;'
    TD1_html = '<TD style="%s">%s</TD>' % (TD1_style, _status_as_glyph(status))
    TD2_style = 'text-align: right; padding-right: 2px;'
    TD2_html = '<TD style="%s">%s</TD>' % (TD2_style, checkbox_html)
    TABLE_html = '<TABLE><TR>%s%s</TR></TABLE>' % (TD1_html, TD2_html)
    out.write('<TD %s>%s</TD>\n' % (' '.join(TD_attrs), TABLE_html))
    return

def _write_glyph_as_TR(out, status, explain_html, toggleable=False):
    out.write('<TR>\n')
    _write_glyph_box(out, status, toggleable)
    out.write('<TD class="glyph_explain">%s</TD>\n' % explain_html)
    out.write('</TR>\n')
    return

def _explain_TIMEOUT_in_HTML():
    t1 = int(BBSvars.INSTALL_timeout  / 60.0)
    t2 = int(BBSvars.BUILD_timeout    / 60.0)
    t3 = int(BBSvars.CHECK_timeout    / 60.0)
    t4 = int(BBSvars.BUILDBIN_timeout / 60.0)
    if BBSvars.buildtype == "bioc-longtests":
        html = 'CHECK of package took more than ' + \
              '%d minutes' % t3
    elif BBSvars.buildtype in ["workflows", "books"]:
        html = 'INSTALL or BUILD of package took more than '
        if t1 == t2:
            html += '%d minutes' % t1
        else:
            html += '%d or %d minutes, respectively' % (t1, t2)
    else:
        html = 'INSTALL, BUILD, CHECK or BUILD BIN ' + \
               'of package took more than '
        if t1 == t2 and t2 == t3 and t3 == t4:
            html += '%d minutes' % t1
        else:
            html += '%d, %d, %d or %d minutes, respectively' % (t1, t2, t3, t4)
    return html

def _explain_ERROR_in_HTML():
    html = 'Bad DESCRIPTION file or '
    if BBSvars.buildtype == "bioc-longtests":
        html += 'CHECK of package produced errors'
    elif BBSvars.buildtype in ["workflows", "books"]:
        html += 'INSTALL or BUILD of package failed'
    else:
        html += 'INSTALL, BUILD or BUILD BIN of package '
        html += 'failed, or CHECK produced errors'
    return html

def _explain_WARNINGS_in_HTML():
    return 'CHECK of package produced warnings'

def _explain_OK_in_HTML():
    if BBSvars.buildtype == "bioc-longtests":
        html = 'CHECK'
    elif BBSvars.buildtype in ["workflows", "books"]:
        html = 'INSTALL or BUILD'
    else:
        html = 'INSTALL, BUILD, CHECK or BUILD BIN ' + \
               'of package was OK'
    return html

def _explain_NotNeeded_in_HTML():
    return 'INSTALL of package was not needed ' + \
           '(click on glyph to see why)'

def _explain_skipped_in_HTML():
    html = 'CHECK or BUILD BIN ' + \
           'of package was skipped because the BUILD step failed\n'
    return html

def _explain_NA_in_HTML():
    if BBSvars.buildtype == "bioc-longtests":
        html = 'CHECK'
    elif BBSvars.buildtype in ["workflows", "books"]:
        html = 'BUILD'
    else:
        html = 'BUILD, CHECK or BUILD BIN'
    html += ' result is not available because of an anomaly ' + \
            'in the Build System\n'
    return html

### FH: Create checkboxes to select display types
def write_explain_glyph_table(out):
    buildtype = BBSvars.buildtype
    out.write('<FORM action="">\n')
    out.write('<TABLE style="width: 590px; border: solid black 1px; border-collapse: collapse;">\n')
    out.write('<TR>\n')
    out.write('<TD COLSPAN="2" style="font-style: italic; border-bottom: solid black 1px;">')
    out.write('<B>Package status is indicated by one of the following glyphs</B>')
    out.write('</TD>\n')
    out.write('</TR>\n')

    _write_glyph_as_TR(out, "TIMEOUT", _explain_TIMEOUT_in_HTML(), True)

    _write_glyph_as_TR(out, "ERROR", _explain_ERROR_in_HTML(), True)

    if buildtype not in ["workflows", "books"]:
        _write_glyph_as_TR(out, "WARNINGS", _explain_WARNINGS_in_HTML(), True)

    _write_glyph_as_TR(out, "OK", _explain_OK_in_HTML(), True)

    ## "NotNeeded" glyph (only used when "smart STAGE2" is enabled i.e.
    ## when STAGE2 skips installation of target packages not needed by
    ## another target package for build or check).
    #if buildtype not in ["workflows", "books", "bioc-longtests"]:
    #    _write_glyph_as_TR(out, "NotNeeded", _explain_NotNeeded_in_HTML())

    if buildtype != "bioc-longtests":
        _write_glyph_as_TR(out, "skipped", _explain_skipped_in_HTML())

    _write_glyph_as_TR(out, "NA", _explain_NA_in_HTML())

    out.write('<TR>\n')
    out.write('<TD COLSPAN="2" style="font-style: italic; border-top: solid black 1px;">')
    out.write('Click on any glyph in the report below ')
    out.write('to access the detailed report.')
    out.write('</TD>\n')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    out.write('</FORM>\n')
    return


##############################################################################
### Glyph cards (gcards) and gcard lists
##############################################################################

class LeafReportReference:
    def __init__(self, pkg, node_hostname, node_id, stage):
        self.pkg = pkg
        self.node_hostname = node_hostname
        self.node_id = node_id
        self.stage = stage

def _get_all_show_classes():
    status_classes = ['timeout', 'error', 'warnings', 'ok']
    return ['show_%s_gcards' % status for status in status_classes]

def _write_vertical_space(out):
    colspan = BBSreportutils.ncol_to_display(BBSvars.buildtype) + 5
    TD_html = '<TD COLSPAN="%s"></TD>' % colspan
    out.write('<TR class="vertical_space">%s</TR>\n' % TD_html)
    return

def _url_to_pkg_landing_page(pkg):
    buildtype = BBSvars.buildtype
    if buildtype == "cran":
        return "https://cran.rstudio.com/package=%s" % pkg
    bioc_version = BBSvars.bioc_version
    if buildtype == "books":
        return "/books/%s/%s/" % (bioc_version, pkg)
    #if buildtype == "data-annotation":
    #    repo = "data/annotation"
    #elif buildtype == "data-experiment":
    #    repo = "data/experiment"
    #elif buildtype == "workflows":
    #    repo = "workflows"
    #else:
    #    repo = "bioc"
    #url = "/packages/%s/%s/html/%s.html" % (bioc_version, repo, pkg)
    ## Use short URL:
    url = "/packages/%s/%s" % (bioc_version, pkg)
    return url

def _pkgname_as_HTML(pkg, pkgdir=None):
    if pkgdir == None:
        return pkg
    return '<A href="%s/">%s</A>' % (pkgdir, pkg)

def _pkgname_and_version_as_HTML(pkg, version, pkgdir=None, deprecated=False):
    html1 = '<B>%s&nbsp;%s</B>' % (_pkgname_as_HTML(pkg, pkgdir), version)
    if deprecated:
        html1 = '<s>%s</s>' % html1
    url = _url_to_pkg_landing_page(pkg)
    SPANcontent = '(<A href="%s">landing page</A>)' % url
    SPANstyle = 'font-size: smaller; font-style: italic;'
    html2 = '<SPAN style="%s">%s</SPAN>' % (SPANstyle, SPANcontent)
    return '%s&nbsp;&nbsp;%s' % (html1, html2)

def _node_OS_Arch_as_SPAN(node):
    return '<SPAN style="font-size: smaller;">%s&nbsp;/&nbsp;%s</SPAN>' % \
           (node.os_html, node.arch)

def _write_node_spec_as_TD(out, node, spec_html, selected=False):
    TDclasses = node.hostname.replace(".", "_")
    if selected:
        TDclasses += ' selected'
    out.write('<TD class="%s">%s</TD>' % (TDclasses, spec_html))
    return

def _write_pkg_status_as_TD(out, pkg, node, stage,
                            leafreport_ref=None, topdir='.'):
    selected = leafreport_ref != None and \
               pkg == leafreport_ref.pkg and \
               node.node_id == leafreport_ref.node_id and \
               stage == leafreport_ref.stage
    TDclasses = 'status %s %s' % (node.hostname.replace(".", "_"), stage)
    if selected:
        TDclasses += ' selected'
    status = BBSreportutils.get_pkg_status(pkg, node.node_id, stage)
    if status in ["skipped", "NA"]:
        TDcontent = _status_as_glyph(status)
    else:
        if leafreport_ref != None:
            pkgdir = '.'
        else:
            pkgdir = '%s/%s' % (topdir, pkg)
        url = BBSreportutils.get_leafreport_rel_url(pkgdir, node.node_id, stage)
        TDcontent = _make_link_with_mouseover(url, _status_as_glyph(status))
    out.write('<TD class="%s">%s</TD>' % (TDclasses, TDcontent))
    return

def write_stagelabel_as_TD(out, stage, leafreport_ref):
    selected = leafreport_ref != None and \
               stage == leafreport_ref.stage
    TDclasses = 'STAGE %s' % stage
    if selected:
        TDclasses += ' selected'
    stage_label = BBSreportutils.stage_label(stage)
    TD_html = '<TD class="%s">%s</TD>' % (TDclasses, stage_label)
    out.write(TD_html)
    return

def write_pkg_stagelabels_as_TDs(out, leafreport_ref=None):
    buildtype = BBSvars.buildtype
    for stage in BBSreportutils.stages_to_display(buildtype):
        write_stagelabel_as_TD(out, stage, leafreport_ref)
    if BBSreportutils.display_propagation_status(buildtype):
        out.write('<TD style="width: 12px;"></TD>')
    return

def write_pkg_propagation_status_as_TD(out, pkg, node):
    status = BBSreportutils.get_propagation_status_from_db(pkg, node.hostname)
    if status == None:
        TDcontent = ''
    else:
        IMGstyle = 'border: 0px; width: 10px; height: 10px;'
        if "/" in out.name:
            path = "../"
        else:
            path = "./"
        if status.startswith("YES"):
            color = "Green"
        elif status.startswith("NO"):
            color = "Red"
        else: # "UNNEEDED"
            color = "Blue"
        IMGsrc = '%s120px-%s_Light_Icon.svg.png' % (path, color)
        TDcontent = '<IMG style="%s" alt="%s" title="%s" src="%s">' % \
                    (IMGstyle, status, status, IMGsrc)
    out.write('<TD class="status %s">%s</TD>' % \
              (node.hostname.replace(".", "_"), TDcontent))
    return

def write_pkg_statuses_as_TDs(out, pkg, node,
                              leafreport_ref=None, topdir='.'):
    TDclasses = 'status %s' % node.hostname.replace(".", "_")
    buildtype = BBSvars.buildtype
    if pkg in skipped_pkgs:
        TDattrs = 'COLSPAN="%s" class="%s"' % \
                  (BBSreportutils.ncol_to_display(buildtype), TDclasses)
        TDcontent = '<SPAN class=%s>&nbsp;%s&nbsp;</SPAN>' % ('ERROR', 'ERROR')
        TDcontent += ' (Bad DESCRIPTION file)'
        out.write('<TD %s>%s</TD>' % (TDattrs, TDcontent))
    elif not BBSreportutils.is_supported(pkg, node):
        TDattrs = 'COLSPAN="%s" class="%s"' % \
                  (BBSreportutils.ncol_to_display(buildtype), TDclasses)
        TDcontent = '... NOT SUPPORTED ...'
        TDcontent = '%s' % TDcontent.replace(' ', '&nbsp;')
        out.write('<TD %s>%s</TD>' % (TDattrs, TDcontent))
    else:
        for stage in BBSreportutils.stages_to_display(buildtype):
            if stage != 'buildbin' or BBSreportutils.is_doing_buildbin(node):
                _write_pkg_status_as_TD(out, pkg, node, stage,
                                        leafreport_ref, topdir)
            else:
                out.write('<TD class="%s"></TD>' % TDclasses)
        if BBSreportutils.display_propagation_status(buildtype):
            write_pkg_propagation_status_as_TD(out, pkg, node)
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

### Produce 2 full TRs.
def write_abc_dispatcher_within_gcard_list(out, current_letter):
    ## FH: Need the collapsable_rows class to blend out the alphabetical
    ## selection when "ok" packages are unselected.
    out.write('<TBODY class="abc_dispatcher collapsable_rows">\n')
    _write_vertical_space(out)
    out.write('<TR class="abc">')
    out.write('<TD COLSPAN="2">')
    out.write('<TABLE class="big_letter"><TR><TD>')
    out.write('<A name="%s">%s</A>' % \
              (current_letter, current_letter))
    out.write('</TD></TR></TABLE>')
    out.write('</TD>')
    colspan = BBSreportutils.ncol_to_display(BBSvars.buildtype) + 3
    out.write('<TD COLSPAN="%s">' % colspan)
    write_abc_dispatcher(out, "", current_letter)
    out.write('</TD>')
    out.write('</TR>\n')
    out.write('</TBODY>\n')
    return

def statuses2classes(statuses):
    classes = []
    if "TIMEOUT" in statuses:
        classes.append("timeout")
    if "ERROR" in statuses:
        classes.append("error")
    if "WARNINGS" in statuses:
        classes.append("warnings")
    ## A package is tagged with the "ok" class if it's not tagged with any of
    ## the "timeout", "error" or "warnings". Note that this means that
    ## a package could end up being tagged with the "ok" class even if it
    ## doesn't have any OK in 'statuses' (e.g. if it's unsupported on all
    ## platforms).
    if len(classes) == 0:
        classes = ["ok"]
    return ' '.join(classes)

def write_quickstats_TD(out, quickstats, node, stage):
    stats = quickstats[node.node_id][stage]
    html = '<TABLE class="quickstats"><TR>'
    html += '<TD class="glyph %s">%d</TD>' % ("TIMEOUT", stats[0])
    html += '<TD class="glyph %s">%d</TD>' % ("ERROR", stats[1])
    if stage == 'checksrc':
        html += '<TD class="glyph %s">%d</TD>' % ("WARNINGS", stats[2])
    html += '<TD class="glyph %s">%d</TD>' % ("OK", stats[3])
    # Only relevant when "smart STAGE2" is enabled.
    #if stage == 'install':
    #    html += '<TD class="glyph %s">%d</TD>' % ("NotNeeded", stats[4])
    html += '</TR></TABLE>'
    out.write('<TD>%s</TD>' % html)
    return

### The quick stats span several table rows (TRs).
def write_quickstats(out, quickstats, no_links, selected_node=None):
    out.write('<THEAD class="quickstats">\n')
    out.write('<TR class="header">')
    TDclass = 'leftmost top_left_corner'
    TDstyle = 'padding-left: 0px;'
    out.write('<TD COLSPAN="3" class="%s" style="%s">QUICK STATS</TD>' % \
              (TDclass, TDstyle))
    out.write('<TD>OS&nbsp;/&nbsp;Arch</TD>')
    write_pkg_stagelabels_as_TDs(out)
    out.write('<TD class="rightmost top_right_corner"></TD>')
    out.write('</TR>\n')
    nb_nodes = len(BBSreportutils.NODES)
    last_i = nb_nodes - 1
    for i in range(nb_nodes):
        is_last = i == last_i
        node = BBSreportutils.NODES[i]
        selected = toned_down = False
        TRclasses = node.hostname.replace(".", "_")
        if selected_node != None:
            if selected_node == node.node_id:
                selected = True
                TRclasses += ' selected_row'
            else:
                toned_down = True
                TRclasses += ' toned_down'
        out.write('<TR class="%s">' % TRclasses)
        node_html = node.node_id
        if not toned_down:
            node_html = '<B>%s</B>' % node_html
        if not no_links and nb_nodes != 1 and not selected:
            node_index_file = '%s-index.html' % node.node_id
            node_html = '<A href="%s">%s</A>' % (node_index_file, node_html)
        if is_last:
            TDclass = 'leftmost bottom_left_corner'
        else:
            TDclass = 'leftmost'
        TD_html = '<TD COLSPAN="3" class="%s">%s</TD>' % (TDclass, node_html)
        out.write(TD_html)
        TD_html = '<TD>%s</TD>' % _node_OS_Arch_as_SPAN(node)
        out.write(TD_html)
        buildtype = BBSvars.buildtype
        for stage in BBSreportutils.stages_to_display(buildtype):
            if stage == 'buildbin' and not BBSreportutils.is_doing_buildbin(node):
                out.write('<TD></TD>')
            else:
                write_quickstats_TD(out, quickstats, node, stage)
        if BBSreportutils.display_propagation_status(buildtype):
            out.write('<TD style="width: 12px;"></TD>')
        if is_last:
            out.write('<TD class="rightmost bottom_right_corner"></TD>')
        else:
            out.write('<TD class="rightmost"></TD>')
        out.write('</TR>\n')
    out.write('</THEAD>\n')
    return

### When 'leafreport_ref' is specified, then a list of 1 gcard is generated.
### A non-compact gcard spans several table rows (TRs) grouped in a
### TBODY element.
def write_gcard(out, pkg, pkg_pos, nb_pkgs, leafreport_ref, topdir,
                pkg_statuses, pkg_status_classes):
    out.write('<TBODY class="gcard %s">\n' % pkg_status_classes)
    out.write('<TR class="header">')
    out.write('<TD class="leftmost top_left_corner"></TD>')
    out.write('<TD>Package <B>%d</B>/%d</TD>' % (pkg_pos, nb_pkgs))
    out.write('<TD style="width: 75px;">Hostname</TD>')
    out.write('<TD style="width: 225px;">OS&nbsp;/&nbsp;Arch</TD>')
    write_pkg_stagelabels_as_TDs(out, leafreport_ref)
    out.write('<TD class="rightmost top_right_corner"></TD>')
    out.write('</TR>\n')
    nb_nodes = len(BBSreportutils.NODES)
    is_first = True
    last_i = nb_nodes - 1
    for i in range(nb_nodes):
        is_last = i == last_i
        node = BBSreportutils.NODES[i]
        selected = toned_down = False
        if leafreport_ref == None or leafreport_ref.node_id == None:
            TRattrs = ''
        elif node.node_id == leafreport_ref.node_id:
            selected = True
            TRattrs = ' class="selected_row"'
        else:
            toned_down = True
            TRattrs = ' class="toned_down"'
        out.write('<TR%s>' % TRattrs)
        if is_last:
            TDattrs = 'ROWSPAN="2" class="leftmost bottom_left_corner"'
        else:
            TDattrs = 'class="leftmost"'
        out.write('<TD %s></TD>' % TDattrs)
        if is_first:
            is_first = False
            if len(pkg_statuses) != 0:
                dcf_record = meat_index[pkg]
                version = dcf_record['Version']
                maintainer = dcf_record['Maintainer']
                status = dcf_record.get('PackageStatus')
            else:
                version = maintainer = status = ''
            deprecated = status == "Deprecated"
            TDstyle = 'vertical-align: top;'
            out.write('<TD ROWSPAN="%d" style="%s">' % (nb_nodes, TDstyle))
            if leafreport_ref == None:
                pkgdir = '%s/%s' % (topdir, pkg)
            elif leafreport_ref.node_id != None:
                pkgdir = '.'
            else:
                pkgdir = None
            html = _pkgname_and_version_as_HTML(pkg, version, pkgdir,
                                                deprecated)
            out.write(html)
            out.write('<BR>%s' % maintainer)
            if (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
                out.write('<BR>')
                write_vcs_meta_for_pkg_as_TABLE(out, pkg,
                                                leafreport_ref != None)
            out.write('</TD>')
        node_html = node.node_id
        if not toned_down:
            node_html = '<B>%s</B>' % node_html
        _write_node_spec_as_TD(out, node, node_html, selected)
        _write_node_spec_as_TD(out, node, _node_OS_Arch_as_SPAN(node))
        write_pkg_statuses_as_TDs(out, pkg, node, leafreport_ref, topdir)
        if is_last:
            TDattrs = 'ROWSPAN="2" class="rightmost bottom_right_corner"'
        else:
            TDattrs = 'class="rightmost"'
        out.write('<TD %s></TD>' % TDattrs)
        out.write('</TR>\n')
    out.write('<TR class="footer">')
    colspan = BBSreportutils.ncol_to_display(BBSvars.buildtype) + 3
    out.write('<TD COLSPAN="%d"></TD>' % colspan)
    out.write('</TR>\n')
    out.write('</TBODY>\n')
    return

def write_gcard_list(out, allpkgs,
                     quickstats=None, no_quickstats_links=False,
                     alphabet_dispatch=False,
                     leafreport_ref=None, topdir='.'):
    full_list = not leafreport_ref
    TABLEclasses = 'gcard_list'
    if full_list:
        TABLEclasses += ' %s' % ' '.join(_get_all_show_classes())
        TABLEattrs = 'class="%s" id="THE_BIG_GCARD_LIST"' % TABLEclasses
    else:
        TABLEattrs = 'class="%s"' % TABLEclasses
    out.write('<TABLE %s>\n' % TABLEattrs)
    nb_pkgs = len(allpkgs)
    if quickstats != None:
        write_quickstats(out, quickstats, no_quickstats_links)
        out.write('<TBODY>\n')
        _write_vertical_space(out)
        out.write('</TBODY>\n')
    pkg_pos = 0
    current_letter = None
    for pkg in allpkgs:
        pkg_pos += 1
        if full_list:
            if alphabet_dispatch:
                first_letter = pkg[0:1].upper()
                if first_letter != current_letter:
                    current_letter = first_letter
                    write_abc_dispatcher_within_gcard_list(out, current_letter)
            pkg_statuses = BBSreportutils.get_distinct_pkg_statuses(pkg)
            if pkg in skipped_pkgs:
                pkg_status_classes = 'error'
            else:
                pkg_status_classes = statuses2classes(pkg_statuses)
            out.write('<TBODY class="gcard_separator %s">\n' % \
                      pkg_status_classes)
            _write_vertical_space(out)
            out.write('</TBODY>\n')
        elif pkg == leafreport_ref.pkg:
            # Display gcard for that package only.
            pkg_statuses = BBSreportutils.get_distinct_pkg_statuses(pkg)
            if pkg in skipped_pkgs:
                pkg_status_classes = 'error'
            else:
                pkg_status_classes = statuses2classes(pkg_statuses)
        else:
            continue
        write_gcard(out, pkg, pkg_pos, nb_pkgs, leafreport_ref, topdir,
                    pkg_statuses, pkg_status_classes)
    out.write('</TABLE>\n')
    return


##############################################################################
### Compact gcards (used for the single node reports)
##############################################################################

### Produces one full TR.
def write_compact_gcard_header(out):
    ## Using the collapsable_rows class here too to blend out the alphabetical
    ## selection + this header when "ok" packages are unselected.
    out.write('<TBODY class="collapsable_rows">\n')
    out.write('<TR class="header">')
    out.write('<TD></TD>')
    out.write('<TD>Package</TD>')
    out.write('<TD COLSPAN="2">Maintainer</TD>')
    write_pkg_stagelabels_as_TDs(out)
    out.write('<TD></TD>')
    out.write('</TR>\n')
    out.write('</TBODY>\n')
    return

### Produces one full TR.
def write_compact_gcard(out, pkg, node, pkg_pos, nb_pkgs):
    pkg_statuses = BBSreportutils.get_distinct_pkg_statuses(pkg, [node])
    if pkg in skipped_pkgs:
        pkg_status_classes = 'error'
    else:
        pkg_status_classes = statuses2classes(pkg_statuses)
    TBODYclasses = 'compact gcard %s' % pkg_status_classes
    out.write('<TBODY class="%s">\n' % TBODYclasses)
    if pkg_pos % 2 == 0:
        TRclass = 'even_row_number'
    else:
        TRclass = 'odd_row_number'
    out.write('<TR class="%s">' % TRclass)
    out.write('<TD class="leftmost row_number"><B>%d</B>/%d</TD>' % \
              (pkg_pos, nb_pkgs))
    if len(pkg_statuses) != 0:
        dcf_record = meat_index[pkg]
        version = dcf_record['Version']
        maintainer = dcf_record['Maintainer']
        status = dcf_record.get('PackageStatus')
    else:
        version = status = maintainer = ''
    deprecated = status == "Deprecated"
    TDcontent = _pkgname_and_version_as_HTML(pkg, version, pkg, deprecated)
    out.write('<TD>%s</TD>' % TDcontent)
    out.write('<TD COLSPAN="2">%s</TD>' % maintainer)
    write_pkg_statuses_as_TDs(out, pkg, node)
    out.write('<TD class="rightmost"></TD>')
    out.write('</TR>\n')
    out.write('</TBODY>\n')
    return

### Same as write_gcard_list(), but uses a more compact layout to display
### results for a single node.
### Also, unlike write_gcard_list(), write_compact_gcard_list() always
### displays the full list (no 'leafreport_ref' argument).
def write_compact_gcard_list(out, node, allpkgs,
                             quickstats=None, no_quickstats_links=False,
                             alphabet_dispatch=False):
    nb_pkgs = len(allpkgs)
    TABLEclasses = 'compact gcard_list %s' % ' '.join(_get_all_show_classes())
    out.write('<TABLE class="%s" id="THE_BIG_GCARD_LIST">\n' % TABLEclasses)
    if quickstats != None:
        write_quickstats(out, quickstats, no_quickstats_links, node.node_id)
    out.write('<TBODY>\n')
    _write_vertical_space(out)
    out.write('</TBODY>\n')
    if not alphabet_dispatch:
        write_compact_gcard_header(out)
    pkg_pos = 0
    current_letter = None
    for pkg in allpkgs:
        pkg_pos += 1
        if alphabet_dispatch:
            first_letter = pkg[0:1].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                write_abc_dispatcher_within_gcard_list(out, current_letter)
                write_compact_gcard_header(out)
        write_compact_gcard(out, pkg, node, pkg_pos, nb_pkgs)
    out.write('</TABLE>\n')
    return


##############################################################################
### Simple gcards (only 1 build status glyph per package)
##############################################################################

### Produces one full TR with 5 TDs in it.
def write_simple_gcard_header(out):
    ## Using the collapsable_rows class here too to blend out the alphabetical
    ## selection + this header when "ok" packages are unselected.
    out.write('<TBODY class="collapsable_rows">\n')
    out.write('<TR class="header">')
    out.write('<TD></TD>')
    out.write('<TD>Package</TD>')
    out.write('<TD>Maintainer</TD>')
    out.write('<TD class="STAGE">INSTALL/BUILD/CHECK</TD>')
    out.write('<TD></TD>')
    out.write('</TR>\n')
    out.write('</TBODY>\n')
    return

### Return decorated glyph describing overall package build status.
def make_pkg_build_status_HTML(pkg, statuses, topdir='.'):
    if pkg in skipped_pkgs:
        return '<SPAN class=%s>&nbsp;%s&nbsp;</SPAN>' % ('ERROR', 'ERROR')
    if 'ERROR' in statuses:
        build_status = 'ERROR'
    elif 'TIMEOUT' in statuses:
        build_status = 'TIMEOUT'
    elif 'NA' in statuses:
        build_status = 'NA'
    elif 'WARNINGS' in statuses:
        build_status = 'WARNINGS'
    elif 'OK' in statuses:
        build_status = 'OK'
    else:
        build_status = 'unknown'
    html = _status_as_glyph(build_status)
    if build_status != 'NA':
        pkgdir = '%s/%s' % (topdir, pkg)
        html = _make_link_with_mouseover(pkgdir, html)
    return html

### Produces one full TR with 5 TDs in it.
def write_simple_gcard(out, pkg, pkg_pos, nb_pkgs):
    pkg_statuses = BBSreportutils.get_distinct_pkg_statuses(pkg)
    if pkg in skipped_pkgs:
        pkg_status_classes = 'error'
    else:
        pkg_status_classes = statuses2classes(pkg_statuses)
    TBODYclasses = 'compact gcard %s' % pkg_status_classes
    out.write('<TBODY class="%s">\n' % TBODYclasses)
    if pkg_pos % 2 == 0:
        TRclass = 'even_row_number'
    else:
        TRclass = 'odd_row_number'
    out.write('<TR class="%s">' % TRclass)
    out.write('<TD class="leftmost row_number"><B>%d</B>/%d</TD>' % \
              (pkg_pos, nb_pkgs))
    if len(pkg_statuses) != 0:
        dcf_record = meat_index[pkg]
        version = dcf_record['Version']
        maintainer = dcf_record['Maintainer']
        status = dcf_record.get('PackageStatus')
    else:
        version = status = maintainer = ''
    deprecated = status == "Deprecated"
    TDcontent = _pkgname_and_version_as_HTML(pkg, version, pkg, deprecated)
    out.write('<TD>%s</TD>' % TDcontent)
    out.write('<TD>%s</TD>' % maintainer)
    TDcontent = make_pkg_build_status_HTML(pkg, pkg_statuses)
    out.write('<TD class="status">%s</TD>' % TDcontent)
    out.write('<TD class="rightmost"></TD>')
    out.write('</TR>\n')
    out.write('</TBODY>\n')
    return

### Even more compact layout than write_compact_gcard_list(). Should be much
### faster to load and render.
def write_simple_gcard_list(out, allpkgs, alphabet_dispatch=False):
    nb_pkgs = len(allpkgs)
    TABLEclasses = 'gcard_list %s' % ' '.join(_get_all_show_classes())
    out.write('<TABLE class="%s" id="THE_BIG_GCARD_LIST">\n' % TABLEclasses)
    out.write('<TBODY>\n')
    _write_vertical_space(out)
    out.write('</TBODY>\n')
    if not alphabet_dispatch:
        write_simple_gcard_header(out)
    pkg_pos = 0
    current_letter = None
    for pkg in allpkgs:
        pkg_pos += 1
        if alphabet_dispatch:
            first_letter = pkg[0:1].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                write_abc_dispatcher_within_gcard_list(out, current_letter)
                write_simple_gcard_header(out)
        write_simple_gcard(out, pkg, pkg_pos, nb_pkgs)
    out.write('</TABLE>\n')
    return


##############################################################################
### Leaf reports
##############################################################################

def _get_incoming_raw_result_path(pkg, node_id, stage, suffix):
    filename = '%s.%s-%s' % (pkg, stage, suffix)
    path = os.path.join(BBSvars.central_rdir_path, 'products-in',
                        node_id, stage, filename)
    return path

def _get_outgoing_raw_result_path(pkg, node_id, stage, suffix):
    filename = '%s-%s' % (stage, suffix)
    return os.path.join(pkg, 'raw-results', node_id, filename)

def _get_Rcheck_path(pkg, node_id):
    Rcheck_dir = pkg + ".Rcheck"
    path = os.path.join(BBSvars.central_rdir_path, "products-in",
                        node_id, "checksrc", Rcheck_dir)
    return path

def write_HTML_header(out, page_title=None, css_file=None, js_file=None):
    report_nodes = BBSutils.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(report_nodes)
    out.write('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"')
    out.write(' "http://www.w3.org/TR/html4/loose.dtd">\n')
    out.write('<HTML>\n')
    out.write('<HEAD>\n')
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
    report_nodes = BBSutils.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(report_nodes)
    out.write('<TABLE class="grid_layout"')
    out.write(' style="width: 100%; background: #EEE;"><TR>')
    out.write('<TD style="text-align: left; padding: 5px; vertical-align: middle;">')
    out.write('<I><A href="%s">Back to <B>%s</B></A></I>' % (href, title))
    out.write('</TD>')
    if not no_alphabet_dispatch and current_letter != None:
        out.write('<TD>')
        write_abc_dispatcher(out, href, current_letter, True)
        out.write('</TD>')
    out.write('</TR></TABLE>\n')
    return

def write_timestamp(out):
    out.write('<P class="time_stamp">\n')
    date = bbs.jobs.currentDateString()
    out.write('This page was generated on %s.\n' % date)
    out.write('</P>\n')
    return

def write_motd_asTABLE(out):
    if not 'BBS_REPORT_MOTD' in os.environ:
        return
    motd = os.environ['BBS_REPORT_MOTD']
    if motd == "":
        return
    out.write('<DIV class="motd">\n')
    out.write('<TABLE>')
    out.write('<TR><TD>%s</TD></TR>' % motd)
    out.write('</TABLE>\n')
    out.write('</DIV>\n')
    return

def write_notes_to_developer(out, pkg):
    # Renviron.bioc is expected to be found in BBS_REPORT_PATH which should
    # be the current working directory.
    if BBSvars.buildtype != "bioc" and not os.path.exists('Renviron.bioc'):
        return
    out.write('<DIV class="motd">\n')
    out.write('<TABLE><TR><TD>\n')
    out.write('To the developers/maintainers ')
    out.write('of the %s package:<BR>\n' % pkg)
    if BBSvars.buildtype == "bioc" and os.path.exists('Renviron.bioc'):
        prefix = '- '
    else:
        prefix = ''
    if BBSvars.buildtype == "bioc":
        url = 'https://bioconductor.org/developers/how-to/troubleshoot-build-report/'
        out.write('%sPlease allow up to 24 hours (and sometimes ' % prefix)
        out.write('48 hours) for your latest push to ')
        out.write('git@git.bioconductor.org:packages/%s.git ' % pkg)
        out.write('to<BR>reflect on this report. ')
        out.write('See <I>How and When does the builder pull? ')
        out.write('When will my changes propagate?</I> ')
        out.write('<A href="%s">here</A> for more information.<BR>\n' % url)
    if os.path.exists('Renviron.bioc'):
        out.write('%sMake sure to use the ' % prefix)
        out.write('<A href="../%s">following settings</A> ' % 'Renviron.bioc')
        out.write('in order to reproduce any error ')
        out.write('or warning you see on this page.<BR>\n')
    out.write('</TD></TR></TABLE>\n')
    out.write('</DIV>\n')
    return

def make_package_index_page(pkg, allpkgs, pkg_rev_deps=None):
    report_nodes = BBSutils.getenv('BBS_REPORT_NODES')
    #title = BBSreportutils.make_report_title(report_nodes)

    page_title = 'All results for package %s' % pkg
    out_rURL = os.path.join(pkg, 'index.html')
    out = open(out_rURL, 'w')

    write_HTML_header(out, page_title, '../report.css', '../report.js')
    out.write('<BODY onLoad="initialize();">\n')
    current_letter = pkg[0:1].upper()
    write_goback_asHTML(out, "../index.html", current_letter)
    write_timestamp(out)
    out.write('<H2>%s</H2>\n' % page_title)

    write_motd_asTABLE(out)

    write_notes_to_developer(out, pkg)

    if not no_raw_results:
        raw_results_rel_url = 'raw-results/'
        out.write('<P style="text-align: center;">')
        out.write('<A href="%s">raw results</A>' % raw_results_rel_url)
        out.write('<P>\n')

    leafreport_ref = LeafReportReference(pkg, None, None, None)
    write_gcard_list(out, allpkgs, leafreport_ref=leafreport_ref)

    if BBSvars.buildtype == "bioc" and len(pkg_rev_deps) != 0:
        quickstats = BBSreportutils.compute_quickstats(pkg_rev_deps)
        out.write('<H3 style="padding: 18px;">')
        out.write('Results for Bioconductor software packages ')
        out.write('that depend directly on package %s' % pkg)
        out.write('</H3>\n')
        write_gcard_list(out, pkg_rev_deps,
                         quickstats=quickstats, no_quickstats_links=True,
                         topdir='..')

    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

def write_Summary_asHTML(out, node_hostname, pkg, node_id, stage):
    out.write('<HR>\n<H3>Summary</H3>\n')
    filepath = _get_incoming_raw_result_path(pkg, node_id, stage, 'summary.dcf')
    if not no_raw_results:
        dest = _get_outgoing_raw_result_path(pkg, node_id, stage, 'summary.dcf')
        shutil.copyfile(filepath, dest)
    summary = bbs.parse.parse_DCF(filepath, merge_records=True)
    out.write('<DIV class="%s hscrollable">\n' % \
              node_hostname.replace(".", "_"))
    out.write('<TABLE>\n')
    for key, value in summary.items():
        if key == 'Status':
            value = _status_as_glyph(value)
        out.write('<TR><TD><B>%s</B>: %s</TD></TR>\n' % (key, value))
    out.write('</TABLE>\n')
    out.write('</DIV>\n')
    return

def write_info_dcf(pkg, node_id):
    filename = 'git-log-%s.dcf' % (pkg)
    filepath = os.path.join(BBSvars.central_rdir_path, 'gitlog', filename)
    dest = os.path.join(pkg, 'raw-results', 'info.dcf')
    shutil.copyfile(filepath, dest)
    dcf_record = meat_index[pkg]
    info = {}
    info['Package'] = dcf_record.get('Package', 'NA')
    info['Version'] = dcf_record.get('Version', 'NA')
    info['Maintainer'] = dcf_record.get('Maintainer', 'NA')
    maintainer_email = dcf_record.get('MaintainerEmail', 'NA')
    info['MaintainerEmail'] = maintainer_email.replace('@', ' at ')
    with open(dest, 'a', encoding='utf-8') as dcf:
        for key, value in info.items():
            dcf.write('%s: %s\n' % (key, value))
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
    encoding = BBSutils.getNodeSpec(node_hostname, 'encoding')
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
        html_line = html.escape(line)  # untrusted
        try:
            out.write(html_line)
        except UnicodeEncodeError:
            out.write(html_line.encode(encoding))
    out.write('</PRE>\n')
    out.write('</DIV>')
    return pattern_detected

def write_Command_output_asHTML(out, node_hostname, pkg, node_id, stage):
    if stage == "checksrc" and BBSvars.buildtype == "bioc-longtests":
        out.write('<HR>\n<H3>&apos;R CMD check&apos; output</H3>\n')
    else:
        out.write('<HR>\n<H3>Command output</H3>\n')
    filepath = _get_incoming_raw_result_path(pkg, node_id, stage, 'out.txt')
    if not os.path.exists(filepath):
        out.write('<P class="noresult"><SPAN>')
        out.write('Due to an anomaly in the Build System, this output ')
        out.write('is not available. We apologize for the inconvenience.')
        out.write('</SPAN></P>\n')
        return
    if not no_raw_results:
        dest = _get_outgoing_raw_result_path(pkg, node_id, stage, 'out.txt')
        shutil.copyfile(filepath, dest)
    ## Encoding is unknown so open in binary mode.
    ## write_file_asHTML() will try to decode with bbs.parse.bytes2str()
    f = open(filepath, "rb")
    write_file_asHTML(out, f, node_hostname)
    f.close()
    return

def write_Installation_output_asHTML(out, node_hostname, pkg, node_id):
    out.write('<HR>\n<H3>Installation output</H3>\n')
    Rcheck_path = _get_Rcheck_path(pkg, node_id)
    filename = '00install.out'
    filepath = os.path.join(Rcheck_path, filename)
    if os.path.exists(filepath):
        Rcheck_dir = pkg + ".Rcheck"
        write_filepath_asHTML(out, Rcheck_dir, filename)
        ## Encoding is unknown so open in binary mode.
        ## write_file_asHTML() will try to decode with bbs.parse.bytes2str()
        f = open(filepath, "rb")
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
    Rcheck_path = os.path.join(BBSvars.central_rdir_path, "products-in",
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
    Rcheck_path = os.path.join(BBSvars.central_rdir_path, "products-in",
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
    if BBSvars.buildtype == "bioc-longtests":
        write_Tests_output_asHTML(out, node_hostname, pkg, node_id)
    write_Command_output_asHTML(out, node_hostname, pkg, node_id, stage)
    write_Installation_output_asHTML(out, node_hostname, pkg, node_id)
    if BBSvars.buildtype != "bioc-longtests":
        write_Tests_output_asHTML(out, node_hostname, pkg, node_id)
        write_Example_timings_asHTML(out, node_hostname, pkg, node_id)
    return

def make_LeafReport(leafreport_ref, allpkgs):
    pkg = leafreport_ref.pkg
    node_hostname = leafreport_ref.node_hostname
    node_id = leafreport_ref.node_id
    stage = leafreport_ref.stage
    page_title = '%s results for %s on %s' % \
                 (BBSreportutils.stage_label(stage), pkg, node_id)
    out_rURL = BBSreportutils.get_leafreport_rel_path(pkg, node_id, stage)
    out = open(out_rURL, 'w')

    write_HTML_header(out, page_title, '../report.css', '../report.js')
    out.write('<BODY onLoad="initialize();">\n')
    current_letter = pkg[0:1].upper()
    write_goback_asHTML(out, "../index.html", current_letter)
    write_timestamp(out)
    out.write('<H2><SPAN class="%s">%s</SPAN></H2>\n' % \
              (node_hostname.replace(".", "_"), page_title))

    write_motd_asTABLE(out)

    write_notes_to_developer(out, pkg)

    if not no_raw_results:
        raw_results_rel_url = 'raw-results/'
        out.write('<P style="text-align: center;">')
        out.write('<A href="%s">raw results</A>' % raw_results_rel_url)
        out.write('<P>\n')

    write_gcard_list(out, allpkgs, leafreport_ref=leafreport_ref)

    status = BBSreportutils.get_pkg_status(pkg, node_id, stage)
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
    print("BBS> [make_node_LeafReports] Node %s: BEGIN ..." % node.node_id)
    sys.stdout.flush()
    for pkg in BBSreportutils.supported_pkgs(node):

        if not no_raw_results:
            os.mkdir(os.path.join(pkg, 'raw-results', node.node_id))

        # INSTALL leaf-report
        if BBSvars.buildtype != "bioc-longtests":
            stage = "install"
            status = BBSreportutils.get_pkg_status(pkg, node.node_id, stage)
            if status != "skipped":
                leafreport_ref = LeafReportReference(pkg,
                                                     node.hostname,
                                                     node.node_id,
                                                     stage)
                make_LeafReport(leafreport_ref, allpkgs)
                if not no_raw_results:
                    write_info_dcf(pkg, node.node_id)

        # BUILD leaf-report
        stage = "buildsrc"
        status = BBSreportutils.get_pkg_status(pkg, node.node_id, stage)
        if not status in ["skipped", "NA"]:
            leafreport_ref = LeafReportReference(pkg,
                                                 node.hostname,
                                                 node.node_id,
                                                 stage)
            make_LeafReport(leafreport_ref, allpkgs)

        # CHECK leaf-report
        if BBSvars.buildtype not in ["workflows", "books"]:
            stage = 'checksrc'
            status = BBSreportutils.get_pkg_status(pkg, node.node_id, stage)
            if not status in ["skipped", "NA"]:
                leafreport_ref = LeafReportReference(pkg,
                                                     node.hostname,
                                                     node.node_id,
                                                     stage)
                make_LeafReport(leafreport_ref, allpkgs)

        # BUILD BIN leaf-report
        if BBSreportutils.is_doing_buildbin(node):
            stage = "buildbin"
            status = BBSreportutils.get_pkg_status(pkg, node.node_id, stage)
            if not status in ["skipped", "NA"]:
                leafreport_ref = LeafReportReference(pkg,
                                                     node.hostname,
                                                     node.node_id,
                                                     stage)
                make_LeafReport(leafreport_ref, allpkgs)

    print("BBS> [make_node_LeafReports] Node %s: END." % node.node_id)
    sys.stdout.flush()
    return

def make_all_LeafReports(allpkgs, allpkgs_inner_rev_deps=None):
    print("BBS> [make_all_LeafReports] Current working dir '%s'" % os.getcwd())
    print("BBS> [make_all_LeafReports] Creating report package subfolders " + \
          "and populating them with index.html files ...", end=" ")
    sys.stdout.flush()
    for pkg in allpkgs:
        os.mkdir(pkg)
        if not no_raw_results:
            os.mkdir(os.path.join(pkg, 'raw-results'))
        if allpkgs_inner_rev_deps != None:
            pkg_rev_deps = allpkgs_inner_rev_deps[pkg]
        else:
            pkg_rev_deps = None
        make_package_index_page(pkg, allpkgs, pkg_rev_deps)
    print("OK")
    sys.stdout.flush()
    for node in BBSreportutils.NODES:
        make_node_LeafReports(allpkgs, node)
    return


##############################################################################
### Main page: HTML stuff above main table
##############################################################################

def write_BioC_mainpage_top_asHTML(out, top_right_html=None):
    report_nodes = BBSutils.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(report_nodes)
    write_HTML_header(out, None, 'report.css', 'report.js')
    ## FH: Initialize the checkboxes when page is (re)loaded
    out.write('<BODY onLoad="initialize();">\n')
    if top_right_html != None:
        out.write('<P style="margin: 0px; text-align: right">%s</P>\n' % \
                  top_right_html)
    out.write('<H1>%s</H1>\n' % title)
    if BBSvars.buildtype == "bioc-longtests":
        long_tests_howto_url = '/developers/how-to/long-tests/'
        out.write('<P style="text-align: center;">')
        out.write('See <A href="%s">here</A> ' % long_tests_howto_url)
        out.write('for how to subscribe to these builds.</P>\n')
    write_timestamp(out)
    write_motd_asTABLE(out)
    if (BBSvars.MEAT0_type == 1 or BBSvars.MEAT0_type == 3):
        out.write('<DIV class="svn_info">\n')
        out.write('<TABLE class="centered"><TR><TD>\n')
        if BBSvars.MEAT0_type == 1:
            vcs = 'svn'
            heading = 'svn info'
            out.write('<P style="text-align: center;">%s</P>\n' % heading)
        #else:
        #    vcs = 'git'
        #    heading = 'git log'
        #    out.write('<P style="text-align: center;">%s</P>\n' % heading)
        write_vcs_meta_for_pkg_as_TABLE(out, None, True)
        out.write('</TD></TR></TABLE>\n')
        out.write('</DIV>\n')
    return

def write_CRAN_mainpage_top_asHTML(out, top_right_html=None):
    report_nodes = BBSutils.getenv('BBS_REPORT_NODES')
    title = BBSreportutils.make_report_title(report_nodes)
    write_HTML_header(out, None, 'report.css', 'report.js')
    out.write('<BODY onLoad="initialize();">\n')
    if top_right_html != None:
        out.write('<P style="text-align: right">%s</P>\n' % top_right_html)
    out.write('<H1>%s</H1>\n' % title)
    write_timestamp(out)
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
    val = bbs.parse.get_next_DCF_val(dcf, var, True)
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
    page_title = 'More about %s' % node.node_id
    NodeInfo_page_path = '%s-NodeInfo.html' % node.node_id
    out = open(NodeInfo_page_path, 'w')

    write_HTML_header(out, page_title, 'report.css')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    write_timestamp(out)
    out.write('<H2><SPAN class="%s">%s</SPAN></H2>\n' % \
              (node.hostname.replace(".", "_"), page_title))
    out.write('<BR>\n')

    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    out.write('<TABLE>\n')
    out.write('<TR><TD><B>Hostname:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.hostname)
    out.write('<TR><TD><B>OS:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.os_html)
    out.write('<TR><TD><B>Arch:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.arch)
    out.write('<TR><TD><B>Platform:&nbsp;</B></TD><TD>%s</TD></TR>\n' % node.platform)
    out.write('<TR><TD><B>R&nbsp;version:&nbsp;</B></TD><TD>%s</TD></TR>\n' % read_Rversion(Node_rdir))
    out.write('<TR>')
    out.write('<TD><B>R&nbsp;environment&nbsp;variables:&nbsp;</B></TD>')
    out.write('<TD>')
    # Renviron.bioc is expected to be found in BBS_REPORT_PATH which should
    # be the current working directory.
    if os.path.exists('Renviron.bioc'):
        out.write('<A href="%s">%s</A>' % ('Renviron.bioc', 'Renviron.bioc'))
    else:
        out.write('none')
    out.write('</TD>')
    out.write('</TR>\n')
    out.write('</TABLE>\n')
    out.write('</DIV>\n')

    out.write('<HR>\n')

    out.write('<H2>C compiler</H2>\n')
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    C_vars = ['CC', 'CFLAGS', 'CPICFLAGS']
    write_Rconfig_table_from_file(out, Node_rdir, C_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CC')
    out.write('</DIV>\n')

    out.write('<HR>\n')

    out.write('<H2>C++ compiler</H2>\n')
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    Cplusplus_vars = ['CXX', 'CXXFLAGS', 'CXXPICFLAGS']
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

    out.write('<H2>C++17 compiler</H2>\n')
    out.write('<DIV class="%s">\n' % node.hostname.replace(".", "_"))
    Cplusplus17_vars = ['CXX17', 'CXX17FLAGS', 'CXX17PICFLAGS', 'CXX17STD']
    write_Rconfig_table_from_file(out, Node_rdir, Cplusplus17_vars)
    write_SysCommandVersion_from_file(out, Node_rdir, 'CXX17')
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
    page_title = 'R packages installed on %s' % node.node_id
    Rinstpkgs_page = '%s-R-instpkgs.html' % node.node_id
    out = open(Rinstpkgs_page, 'w')

    write_HTML_header(out, page_title, 'report.css')
    out.write('<BODY>\n')
    write_goback_asHTML(out, "./index.html")
    write_timestamp(out)
    out.write('<H2><SPAN class="%s">%s</SPAN></H2>\n' % \
              (node.hostname.replace(".", "_"), page_title))
    out.write('<BR>\n')

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
    products_in_rdir = BBSvars.products_in_rdir
    for node in BBSreportutils.NODES:
        Node_rdir = products_in_rdir.subdir(node.node_id)
        NodeInfo_page_path = make_NodeInfo_page(Node_rdir, node)
        Rversion_html = read_Rversion(Node_rdir)
        Rinstpkgs_strings = make_Rinstpkgs_page(Node_rdir, node)
        out.write('<TR class="%s">' % node.hostname.replace(".", "_"))
        out.write('<TD><B><A href="%s"><B>%s</B></A></B></TD>' % (NodeInfo_page_path, node.node_id))
        out.write('<TD>%s</TD>' % node.os_html)
        out.write('<TD>%s</TD>' % node.arch)
        out.write('<TD>%s</TD>' % node.platform)
        out.write('<TD>%s</TD>' % Rversion_html)
        out.write('<TD style="text-align: right;">')
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

def write_glyph_and_propagation_LED_table(out, hide_LEDs=False):
    out.write('<DIV style="font-size: smaller;">\n')
    out.write('<TABLE style="margin-left: auto; margin-right: auto;"><TR>')
    out.write('<TD style="vertical-align: top;">\n')
    write_explain_glyph_table(out)
    out.write('</TD>')
    if not hide_LEDs:
        out.write('<TD style="vertical-align: top; padding-left: 6px;">\n')
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

def write_node_report(node, allpkgs, quickstats):
    print("BBS> [write_node_report] Node %s: BEGIN ..." % node.node_id)
    sys.stdout.flush()
    node_index_file = '%s-index.html' % node.node_id
    out = open(node_index_file, 'w')
    page_title = "All results on %s" % node.node_id

    write_HTML_header(out, page_title, 'report.css', 'report.js')
    out.write('<BODY onLoad="initialize();">\n')
    write_goback_asHTML(out, "./index.html")
    write_timestamp(out)
    out.write('<H2><SPAN class="%s">%s</SPAN></H2>\n' % \
              (node.hostname.replace(".", "_"), page_title))
    out.write('<BR>\n')

    write_motd_asTABLE(out)

    hide_LEDs = not BBSreportutils.display_propagation_status(BBSvars.buildtype)
    write_glyph_and_propagation_LED_table(out, hide_LEDs)
    out.write('<HR>\n')
    write_compact_gcard_list(out, node,
                             allpkgs, quickstats=quickstats,
                             alphabet_dispatch=not no_alphabet_dispatch)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    print("BBS> [write_node_report] Node %s: END." % node.node_id)
    sys.stdout.flush()
    return node_index_file

def make_all_NodeReports(allpkgs, quickstats):
    if len(BBSreportutils.NODES) != 1:
        for node in BBSreportutils.NODES:
            write_node_report(node, allpkgs, quickstats)
    return


##############################################################################
### Main page (multiple platform report)
##############################################################################

def write_mainpage_asHTML(out, allpkgs, quickstats,
                          simple_layout=False, top_right_html=None):
    if BBSvars.buildtype != "cran":
        write_BioC_mainpage_top_asHTML(out, top_right_html)
    else: # "cran" buildtype
        write_CRAN_mainpage_top_asHTML(out, top_right_html)
    if not simple_layout:
        out.write('<BR>\n')
        write_node_specs_table(out)
    out.write('<BR>\n')
    write_glyph_and_propagation_LED_table(out, hide_LEDs=simple_layout)
    out.write('<HR>\n')
    if simple_layout:
        write_simple_gcard_list(out, allpkgs,
                         alphabet_dispatch=not no_alphabet_dispatch)
    elif len(BBSreportutils.NODES) == 1:
        write_compact_gcard_list(out, BBSreportutils.NODES[0], allpkgs,
                         quickstats=quickstats,
                         alphabet_dispatch=not no_alphabet_dispatch)
    else:
        write_gcard_list(out, allpkgs,
                         quickstats=quickstats,
                         alphabet_dispatch=not no_alphabet_dispatch)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    return

def make_BioC_MainReport(allpkgs, quickstats, simple_layout=False):
    print("BBS> [make_BioC_MainReport] BEGIN ...")
    sys.stdout.flush()
    top_right_html = None
    out = open('index.html', 'w')
    if simple_layout:
        top_right_html = '<A href="long-report.html">Long report</A>'
    write_mainpage_asHTML(out, allpkgs, quickstats,
                          simple_layout, top_right_html)
    out.close()
    if simple_layout:
        out = open('long-report.html', 'w')
        top_right_html = '<A href="./">Simplified report</A>'
        write_mainpage_asHTML(out, allpkgs, quickstats, False, top_right_html)
        out.close()
    print("BBS> [make_BioC_MainReport] END.")
    sys.stdout.flush()
    return

def make_CRAN_MainReport(allpkgs, quickstats, simple_layout=False):
    print("BBS> [make_CRAN_MainReport] BEGIN ...")
    top_right_html = None
    out = open('index.html', 'w')
    if simple_layout:
        top_right_html = '<A href="long-report.html">Long report</A>'
    write_mainpage_asHTML(out, allpkgs, quickstats,
                          simple_layout, top_right_html)
    out.close()
    if simple_layout:
        out = open('long-report.html', 'w')
        top_right_html = '<A href="./">Simplified report</A>'
        write_mainpage_asHTML(out, allpkgs, quickstats, False, top_right_html)
        out.close()
    print("BBS> [make_CRAN_MainReport] END.")
    sys.stdout.flush()
    return


##############################################################################
### MAIN SECTION
##############################################################################

### Return a dict with 2 key->value pairs:
###   Key                       Value
###   'no-alphabet-dispatch' -> True or False
###   'no-raw-results'      -> True or False
def parse_options(argv):
    usage_msg = 'Usage:\n' + \
        '    BBS-report.py [simple-layout] [no-alphabet-dispatch] [no-raw-results]\n'
    valid_options = ['simple-layout', 'no-alphabet-dispatch', 'no-raw-results']
    argv = set(argv[1:])
    if not argv.issubset(valid_options):
        sys.exit(usage_msg)
    options = {}
    for option in valid_options:
        options[option] = option in argv
    return options

if __name__ == "__main__":
    options = parse_options(sys.argv)
    print()
    if not os.path.isfile(BBSreportutils.BUILD_STATUS_DB_file):
        print('mmh.. I don\'t see the \'%s\' file in the current directory!' \
              % BBSreportutils.BUILD_STATUS_DB_file)
        print('Make sure to be in \'%s/\' ' % BBSvars.Central_rdir.path)
        print('before running the BBS-report.py script.')
        sys.exit('=> EXIT.')

    print('BBS> ==============================================================')
    print("BBS> [stage6d] STARTING stage6d at %s..." % time.asctime())
    sys.stdout.flush()

    simple_layout = options['simple-layout']
    no_alphabet_dispatch = options['no-alphabet-dispatch']
    no_raw_results = options['no-raw-results']
    report_nodes = BBSutils.getenv('BBS_REPORT_NODES')
    report_path = BBSutils.getenv('BBS_REPORT_PATH')
    r_environ_user = BBSutils.getenv('R_ENVIRON_USER', is_required=False)
    css_file = BBSutils.getenv('BBS_REPORT_CSS', is_required=False)
    bgimg_file = BBSutils.getenv('BBS_REPORT_BGIMG', is_required=False)
    js_file = BBSutils.getenv('BBS_REPORT_JS', is_required=False)

    print("BBS> [stage6d] remake_dir %s" % report_path)
    bbs.fileutils.remake_dir(report_path)

    print("BBS> [stage6d] cp %s %s/" % \
          (BBSutils.meat_index_file, report_path))
    shutil.copy(BBSutils.meat_index_file, report_path)

    print("BBS> [stage6d] cp %s %s/" % \
          (BBSutils.skipped_index_file, report_path))
    shutil.copy(BBSutils.skipped_index_file, report_path)

    print("BBS> [stage6d] cp %s %s/" % \
          (BBSreportutils.BUILD_STATUS_DB_file, report_path))
    shutil.copy(BBSreportutils.BUILD_STATUS_DB_file, report_path)

    if os.path.exists(BBSreportutils.PROPAGATION_STATUS_DB_file):
        print("BBS> [stage6d] cp %s %s/" % \
              (BBSreportutils.PROPAGATION_STATUS_DB_file, report_path))
        shutil.copy(BBSreportutils.PROPAGATION_STATUS_DB_file, report_path)

    print("BBS> [stage6d] cd %s/" % report_path)
    os.chdir(report_path)

    BBSreportutils.write_htaccess_file()

    BBSreportutils.set_NODES(report_nodes)

    ## Compute 'meat_index' (dict), 'skipped_pkgs' (list),
    ## and 'allpkgs' (list).
    meat_index = bbs.parse.get_meat_packages(BBSutils.meat_index_file,
                                             as_dict=True)
    skipped_pkgs = bbs.parse.get_meat_packages(BBSutils.skipped_index_file)
    allpkgs = list(meat_index.keys()) + skipped_pkgs
    allpkgs.sort(key=str.lower)

    print("BBS> [stage6d] Import package statuses from %s ..." % \
          BBSreportutils.BUILD_STATUS_DB_file, end=" ")
    sys.stdout.flush()
    allpkgs_quickstats = BBSreportutils.import_BUILD_STATUS_DB(allpkgs)
    print("OK")
    sys.stdout.flush()

    ## Set 'allpkgs_inner_rev_deps'.
    if BBSvars.buildtype == "bioc":
        ## Load package dep graph.
        node0 = BBSreportutils.NODES[0]
        Node0_rdir = BBSvars.products_in_rdir.subdir(node0.node_id)
        print("BBS> [stage6d] Get %s from %s/" % \
              (BBSutils.pkg_dep_graph_file, Node0_rdir.label))
        Node0_rdir.Get(BBSutils.pkg_dep_graph_file)
        print("BBS> [stage6d] Loading %s file ..." % \
              BBSutils.pkg_dep_graph_file, end=" ")
        sys.stdout.flush()
        pkg_dep_graph = bbs.parse.load_pkg_dep_graph(BBSutils.pkg_dep_graph_file)
        print("OK")
        allpkgs_inner_rev_deps = BBSreportutils.get_inner_reverse_deps(
                                     allpkgs,
                                     pkg_dep_graph)
        sys.stdout.flush()
    else:
        allpkgs_inner_rev_deps = None

    if r_environ_user != None:
        dst = os.path.join(report_path, 'Renviron.bioc')
        print("BBS> [stage6d] cp %s %s" % (r_environ_user, dst))
        shutil.copy(r_environ_user, dst)

    if css_file != None:
        print("BBS> [stage6d] cp %s %s/" % (css_file, report_path))
        shutil.copy(css_file, report_path)

    if bgimg_file != None:
        print("BBS> [stage6d] cp %s %s/" % (bgimg_file, report_path))
        shutil.copy(bgimg_file, report_path)

    if js_file != None:
        print("BBS> [stage6d] cp %s %s/" % (js_file, report_path))
        shutil.copy(js_file, report_path)

    for color in ["Red", "Green", "Blue"]:
        icon = "%s/images/120px-%s_Light_Icon.svg.png" % \
               (os.getenv("BBS_HOME"), color)
        shutil.copy(icon, report_path)

    print("BBS> [stage6d] Will generate HTML report for nodes: %s" % \
          report_nodes)
    make_all_LeafReports(allpkgs, allpkgs_inner_rev_deps)
    make_all_NodeReports(allpkgs, allpkgs_quickstats)
    if BBSvars.buildtype != "cran":
        make_BioC_MainReport(allpkgs, allpkgs_quickstats, simple_layout)
    else: # "cran" buildtype
        make_CRAN_MainReport(allpkgs, allpkgs_quickstats, simple_layout)

    print("BBS> [stage6d] DONE at %s." % time.asctime())

