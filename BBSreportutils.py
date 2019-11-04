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
        title = "Long tests"
    elif subbuilds == "workflows":
        title = "Workflows build"
    else:
        nnodes = 0
        for node in report_nodes.split(' '):
            if node == "":
                continue
            nnodes += 1
        if nnodes != 1:
            title = "Multiple platform build/check"
        else:
            title = "Build/check"
    title += " report for "
    if subbuilds == "cran":
        title += "CRAN"
    else:
        bioc_version = BBScorevars.getenv('BBS_BIOC_VERSION', False)
        title += "BioC %s" % bioc_version
        if subbuilds == "data-annotation":
            title += " annotations"
        elif subbuilds == "data-experiment":
            title += " experimental data"
    return title

## Stages to display on report (as columns in HTML table).
def stages_to_display(subbuilds):
    if subbuilds == "bioc-longtests":
        return ['checksrc']  # we run 'buildsrc' but don't display it
    if subbuilds == "workflows":
        return ['install', 'buildsrc']
    return ['install', 'buildsrc', 'checksrc', 'buildbin']

def stage_label(stage):
    stage2label = {
        'install':  "INSTALL",
        'buildsrc': "BUILD",
        'checksrc': "CHECK",
        'buildbin': "BUILD BIN"
    }
    return stage2label[stage]


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

def get_status_from_db(pkg, node_id, stage):
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
        stages = stages_to_display()
        if 'buildbin' in stages and not is_doing_buildbin(node):
            stages.remove('buildbin')
        for stage in stages:
            status = get_status_from_db(pkg, node.id, stage)
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

