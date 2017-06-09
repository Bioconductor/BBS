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
### urllib.urlopen() doesn't raise an error when the object is not found (HTTP
### Error 404) but urllib2.urlopen() does (raises an urllib2.HTTPError object)
import urllib2 

import bbs.parse
import BBSvars
import BBScorevars


bioc_version = BBScorevars.getenv('BBS_BIOC_VERSION', False)

STATUS_DB_file = 'STATUS_DB.txt'
PROPAGATE_STATUS_DB_file = '../PROPAGATE_STATUS_DB.txt'

### Can be 'local' or the URL where to download the data from
data_source = 'local'


def map_package_type_to_outgoing_node(package_type):
    map = {}
    rawmap = os.getenv("BBS_OUTGOING_MAP")
    segs = rawmap.split(" ")
    for seg in segs:
        key = seg.split(":")[0]
        value = seg.split(":")[1].split("/")[0]
        map[key] = value
    return(map[package_type])

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
    return(map[node])


### Open read-only data stream ('local' or 'published')
def open_rodata(file):
    if data_source == 'local':
        return { 'rostream': open(file, 'r'), 'desc': file }
    url = '%s/%s' % (data_source, file)
    return { 'rostream': urllib2.urlopen(url), 'desc': url }

### If 'node_hostname' is specified, then returns only the packages that are
### supported on this node (and the returned list is unsorted).
def get_pkgs(dcf, node_hostname=None, node_id=None):
    if node_hostname:
        pkgType = BBScorevars.getNodeSpec(node_hostname, 'pkgType')
        pkgs = bbs.parse.readPkgsFromDCF(dcf, node_id, pkgType)
    else:
        pkgs = bbs.parse.readPkgsFromDCF(dcf)
        pkgs.sort(lambda x, y: cmp(string.lower(x), string.lower(y)))
    return pkgs

def get_pkgs_from_meat_index(node_hostname=None, node_id=None):
    rodata = open_rodata(BBScorevars.meat_index_file)
    pkgs = get_pkgs(rodata['rostream'], node_hostname, node_id)
    rodata['rostream'].close()
    return pkgs

def get_pkg_field_from_meat_index(pkg, field):
    rodata = open_rodata(BBScorevars.meat_index_file)
    val = bbs.parse.getPkgFieldFromDCF(rodata['rostream'], pkg, field, rodata['desc'])
    rodata['rostream'].close()
    return val

def get_status(dcf, pkg, node_id, stagecmd):
    key = '%s#%s#%s' % (pkg, node_id, stagecmd)
    status = bbs.parse.getNextDcfVal(dcf, key, full_line=True)
    return status

def get_propagation_status_from_db(pkg, node_id):
    rodata = open_rodata(PROPAGATE_STATUS_DB_file)
    status = get_status(rodata['rostream'], pkg, 
      map_outgoing_node_to_package_type(node_id), 'propagate')
    return(status)

def get_status_from_db(pkg, node_id, stagecmd):
    rodata = open_rodata(STATUS_DB_file)
    status = get_status(rodata['rostream'], pkg, node_id, stagecmd)
    rodata['rostream'].close()
    return status

def get_distinct_statuses_from_db(pkg, nodes=None):
    if nodes == None:
        nodes = NODES
    statuses = []
    for node in nodes:
        if not is_supported(pkg, node):
            continue
        stagecmds = ['install', 'buildsrc', 'checksrc']
        if is_doing_buildbin(node):
            stagecmds.append('buildbin')
        for stagecmd in stagecmds:
            status = get_status_from_db(pkg, node.id, stagecmd)
            if status != "skipped" and status not in statuses:
                statuses.append(status)
    return statuses

def WReadDcfVal(rdir, file, field, full_line=False):
    dcf = rdir.WOpen(file)
    val = bbs.parse.getNextDcfVal(dcf, field, full_line)
    dcf.close()
    return val

### Get svn info for Rpacks/ or Rpacks/pkg/
def get_svn_info(pkg, key):
    Central_rdir = BBScorevars.Central_rdir
    if pkg == None:
        file = "svninfo/svn-info.txt"
    else:
        file = "svninfo/svn-info-%s.txt" % pkg
    val = WReadDcfVal(Central_rdir, file, key, True)
    if val == None:
        raise bbs.parse.DcfFieldNotFoundError(file, key)
    return val

def get_vcs_meta(pkg, key):
    Central_rdir = BBScorevars.Central_rdir
    file = os.path.join(BBSvars.vcsmeta_dir, BBSvars.vcsmeta_file)
    if pkg != None:
        file = "-%s.".join(file.split(".")) % pkg
    val = WReadDcfVal(Central_rdir, file, key, True)
    if val == None:
        raise bbs.parse.DcfFieldNotFoundError(file, key)
    return val

def get_leafreport_rURL(pkg, node_id, stagecmd):
    return "%s/%s-%s.html" % (pkg, node_id, stagecmd)

def get_build_label():
    if BBScorevars.mode == "cran":
        return "CRAN"
    build_label = "BioC %s" % bioc_version
    if BBScorevars.mode == "biocLite":
        build_label = "biocLite (%s)" % build_label
    elif BBScorevars.mode == "data-experiment":
        build_label = "BioC experimental data"
    return build_label



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

