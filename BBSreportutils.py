##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Jan 17, 2008
###

import sys
import os
import string
import urllib.request

import bbs.parse
import BBSvars
import BBScorevars


##############################################################################
###
### The NODES db (in memory)
###
##############################################################################

class Node:

    def __init__(self, hostname, id, os_html, arch, platform, buildbin, pkgs):
        self.hostname = hostname
        self.id = id
        self.os_html = os_html
        self.arch = arch
        self.platform = platform
        self.buildbin = buildbin # boolean
        self.pkgs = pkgs # list of pkg names

### A list of Node objects
NODES = []

def fancyname_has_a_bin_suffix(fancyname):
    ns = fancyname.split(":")
    if ns[0] == "" or len(ns) > 2 or (len(ns) == 2 and ns[1] != "bin"):
        sys.exit("don't know what to report for '%s' => EXIT." % fancyname)
    return len(ns) == 2

def set_NODES(fancynames_in_one_string):
    fancynames = fancynames_in_one_string.split(' ')
    for fancyname in fancynames:
        if fancyname == "":
            continue
        id = fancyname.split(":")[0]
        hostname = id.split("-")[0]
        os_html = BBScorevars.getNodeSpec(hostname, 'OS').replace(' ', '&nbsp;')
        arch = BBScorevars.getNodeSpec(hostname, 'Arch')
        platform = BBScorevars.getNodeSpec(hostname, 'Platform')
        buildbin = fancyname_has_a_bin_suffix(fancyname)
        pkgs = get_pkgs_from_meat_index(hostname, id)
        node = Node(hostname, id, os_html, arch, platform, buildbin, pkgs)
        NODES.append(node)
    if len(NODES) == 0:
        sys.exit("nothing to report (no nodes) => EXIT.")
    return

def is_doing_buildbin(node):
    return node.buildbin

def supported_pkgs(node):
    return node.pkgs

def is_supported(pkg, node):
    return pkg in supported_pkgs(node)

def supported_nodes(pkg):
    nodes = []
    for node in NODES:
        if is_supported(pkg, node):
            nodes.append(node)
    return nodes


##############################################################################
###
### make_report_title()
### stages_to_display()
###
##############################################################################

def make_report_title(subbuilds, report_nodes):
    if subbuilds == "bioc-longtests":
        title = "Long Tests"
    elif subbuilds == "workflows":
        title = "Workflows build"
    elif subbuilds == "books":
        title = "Books build"
    else:
        nnodes = 0
        for node in report_nodes.split(' '):
            if node == "":
                continue
            nnodes += 1
        if subbuilds == "bioc-testing":
            title = '"Blame Jeroen" build/check'
        elif nnodes != 1:
            title = "Multiple platform build/check"
        else:
            title = "Build/check"
    title += " report for "
    if subbuilds == "cran":
        title += "CRAN"
    else:
        title += "BioC %s" % BBScorevars.bioc_version
        if subbuilds == "data-annotation":
            title += " annotations"
        elif subbuilds == "data-experiment":
            title += " experimental data"
    return title

def stage_label(stage):
    stage2label = {
        'install':  "INSTALL",
        'buildsrc': "BUILD",
        'checksrc': "CHECK",
        'buildbin': "BUILD BIN"
    }
    return stage2label[stage]

## Stages to display on the report (as columns in HTML table) for the given
## subbuilds. Should be a subset of the stages that were run because we
## obviously can't display the results for stages that we didn't run.
## However we don't necessarily want to display the results for all the
## stages that we ran. For example, for the "bioc-longtests" subbuilds
## we run 'buildsrc' (STAGE3) and 'checksrc' (STAGE4) but we only display
## the results of 'checksrc' (CHECK column on the report).
def stages_to_display(subbuilds):
    if subbuilds in ["data-annotation", "data-experiment"]:
        return ['install', 'buildsrc', 'checksrc']
    if subbuilds in ["workflows", "books"]:
        return ['install', 'buildsrc']
    if subbuilds == "bioc-longtests":
        return ['checksrc']  # we run 'buildsrc' but don't display it
    return ['install', 'buildsrc', 'checksrc', 'buildbin']

### Whether to display the package propagation status led or not for the
### given subbuilds.
def display_propagation_status(subbuilds):
    return subbuilds not in ["bioc-longtests", "bioc-testing", "cran"]

def ncol_to_display(subbuilds):
    return len(stages_to_display(subbuilds)) + \
           display_propagation_status(subbuilds)


##############################################################################

STATUS_DB_file = 'STATUS_DB.txt'
PROPAGATE_STATUS_DB_file = '../PROPAGATE_STATUS_DB.txt'

### Can be 'local' or the URL where to download the data from
data_source = 'local'


##############################################################################

def map_package_type_to_outgoing_node(package_type):
    map = {}
    rawmap = os.getenv("BBS_OUTGOING_MAP")
    segs = rawmap.split(" ")
    for seg in segs:
        key = seg.split(":")[0]
        value = seg.split(":")[1].split("/")[0]
        map[key] = value
    return map[package_type]

def map_outgoing_node_to_package_type(node):
    map = {}
    rawmap = os.getenv("BBS_OUTGOING_MAP")
    segs = rawmap.split(" ")
    for seg in segs:
        pkgtype, rest = seg.split(":")
        anode = rest.split("/")[0]
        map[anode] = pkgtype
    if (not node in map):
        return None
    return map[node]

### Open read-only data stream ('local' or 'published')
def open_rodata(file):
    if data_source == 'local':
        return { 'rostream': open(file, 'rb'), 'desc': file }
    url = '%s/%s' % (data_source, file)
    return { 'rostream': urllib.request.urlopen(url), 'desc': url }

### If 'node_hostname' is specified, then returns only the packages that are
### supported on this node (and the returned list is unsorted).
def get_pkgs(dcf, node_hostname=None, node_id=None):
    if node_hostname:
        pkgType = BBScorevars.getNodeSpec(node_hostname, 'pkgType')
        pkgs = bbs.parse.readPkgsFromDCF(dcf, node_id, pkgType)
    else:
        pkgs = bbs.parse.readPkgsFromDCF(dcf)
        pkgs.sort(key=str.lower)
    return pkgs

def get_pkgs_from_meat_index(node_hostname=None, node_id=None):
    rodata = open_rodata(BBScorevars.meat_index_file)
    pkgs = get_pkgs(rodata['rostream'], node_hostname, node_id)
    rodata['rostream'].close()
    return pkgs

def get_pkgs_from_skipped_index(node_hostname=None, node_id=None):
    rodata = open_rodata(BBScorevars.skipped_index_file)
    pkgs = get_pkgs(rodata['rostream'], node_hostname, node_id)
    rodata['rostream'].close()
    return pkgs

def get_pkg_field_from_meat_index(pkg, field):
    rodata = open_rodata(BBScorevars.meat_index_file)
    val = bbs.parse.getPkgFieldFromDCF(rodata['rostream'], pkg, field, rodata['desc'])
    rodata['rostream'].close()
    return val

def get_status(dcf, pkg, node_id, stage):
    key = '%s#%s#%s' % (pkg, node_id, stage)
    status = bbs.parse.getNextDcfVal(dcf, key, full_line=True)
    return status

def get_propagation_status_from_db(pkg, node_id):
    try:
        rodata = open_rodata(PROPAGATE_STATUS_DB_file)
    except FileNotFoundError:
        return None
    status = get_status(rodata['rostream'], pkg,
                        map_outgoing_node_to_package_type(node_id),
                        'propagate')
    return status

def _get_status_from_db(pkg, node_id, stage):
    rodata = open_rodata(STATUS_DB_file)
    status = get_status(rodata['rostream'], pkg, node_id, stage)
    rodata['rostream'].close()
    if status == None:
        raise Exception("'%s' status for package %s on %s not found in %s" %
                        (stage, pkg, node_id, STATUS_DB_file))
    return status

def get_distinct_statuses_from_db(pkg, nodes=None):
    if nodes == None:
        nodes = NODES
    statuses = []
    for node in nodes:
        if not is_supported(pkg, node):
            continue
        stages = stages_to_display(BBScorevars.subbuilds)
        if 'buildbin' in stages and not is_doing_buildbin(node):
            stages.remove('buildbin')
        for stage in stages:
            status = _get_status_from_db(pkg, node.id, stage)
            if status != "skipped" and status not in statuses:
                statuses.append(status)
    return statuses

def WReadDcfVal(rdir, file, field, full_line=False):
    dcf = rdir.WOpen(file)
    val = bbs.parse.getNextDcfVal(dcf, field, full_line)
    dcf.close()
    return val

### Get vcs metadata for Rpacks/ or Rpacks/pkg/
def get_vcs_meta(pkg, key):
    Central_rdir = BBScorevars.Central_rdir
    file = BBSvars.vcsmeta_file
    if pkg != None:
        file = "-%s.".join(file.rsplit(".", 1)) % pkg
    val = WReadDcfVal(Central_rdir, file, key, True)
    if val == None:
        raise bbs.parse.DcfFieldNotFoundError(file, key)
    return val

def get_leafreport_rel_path(pkg, node_id, stage):
    return os.path.join(pkg, "%s-%s.html" % (node_id, stage))

def get_leafreport_rel_url(pkg, node_id, stage):
    return "%s/%s-%s.html" % (pkg, node_id, stage)


##############################################################################
###
### import_STATUS_DB()
### get_pkg_status()
###
##############################################################################

STATUS_DB = {}
STATUS_SUMMARY = {}

def _set_pkg_status(pkg, node_id, stage, status):
    if pkg not in STATUS_DB:
        STATUS_DB[pkg] = {}
    if node_id not in STATUS_DB[pkg]:
        STATUS_DB[pkg][node_id] = {}
    STATUS_DB[pkg][node_id][stage] = status
    return

def _update_STATUS_SUMMARY(pkg, node_id, stage, status):
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

def import_STATUS_DB(allpkgs):
    for pkg in allpkgs:
        for node in supported_nodes(pkg):

            # INSTALL status
            if BBScorevars.subbuilds != "bioc-longtests":
                stage = 'install'
                status = _get_status_from_db(pkg, node.id, stage)
                _set_pkg_status(pkg, node.id, stage, status)
                _update_STATUS_SUMMARY(pkg, node.id, stage, status)

            # BUILD status
            stage = 'buildsrc'
            status = _get_status_from_db(pkg, node.id, stage)
            _set_pkg_status(pkg, node.id, stage, status)
            _update_STATUS_SUMMARY(pkg, node.id, stage, status)
            skipped_is_OK = status in ["TIMEOUT", "ERROR"]

            # CHECK status
            if BBScorevars.subbuilds not in ["workflows", "books"]:
                stage = 'checksrc'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = _get_status_from_db(pkg, node.id, stage)
                _set_pkg_status(pkg, node.id, stage, status)
                _update_STATUS_SUMMARY(pkg, node.id, stage, status)

            # BUILD BIN status
            if is_doing_buildbin(node):
                stage = 'buildbin'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = _get_status_from_db(pkg, node.id, stage)
                _set_pkg_status(pkg, node.id, stage, status)
                _update_STATUS_SUMMARY(pkg, node.id, stage, status)
    return STATUS_SUMMARY

def get_pkg_status(pkg, node_id, stage):
    if len(STATUS_DB) == 0:
        sys.exit("You must import package statuses with " + \
                 "BBSreportutils.import_STATUS_DB() before " + \
                 "using BBSreportutils.get_pkg_status() => EXIT.")
    return STATUS_DB[pkg][node_id][stage]

