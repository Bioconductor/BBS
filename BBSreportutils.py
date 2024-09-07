##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Jul 6, 2021
###

import sys
import os
import string
import urllib.request

import bbs.parse
import BBSutils
import BBSvars


##############################################################################
### write_htaccess_file()
##############################################################################

### Placing this .haccess file in the top-level folder of the build report
### will help the various text files (i.e. non-HTML) included in the report
### get properly displayed in a browser. For example, without this .haccess
### file, things like R's beloved fancy quotes that are commonly found in
### "raw result" files will look like garbbage (e.g. â€˜Rhdf5libâ€™) in most
### browsers.
### Note that using the UTF-8 encoding solves most displaying issues but not
### all of them. For example it won't help with charaters from exotic encodings
### that are sometimes found in the meat-index.dcf file (in the Maintainer
### field of some packages).
### Finally note that using this .htaccess file only solves a cosmetic issue
### (i.e. it only affects how the text files included in the report get
### displayed in a browser). Most importantly, these text files are what they
### are and tools like wget or curl will download them as-is, regardless of
### what their original encoding is and regardless of what encoding is
### specified in the .htaccess file.
def write_htaccess_file():
    out = open('.htaccess', 'w')
    out.write('AddCharset UTF-8 .dcf .txt .TXT .log\n')
    out.close()
    return


##############################################################################
###
### The NODES db (in memory)
###
##############################################################################

class Node:

    def __init__(self, hostname, node_id, os_html, arch, platform, buildbin, pkgs):
        self.hostname = hostname
        self.node_id = node_id
        self.os_html = os_html
        self.arch = arch
        self.platform = platform
        self.buildbin = buildbin  # boolean (or None if foreign node)
        self.pkgs = pkgs  # list of pkg names

### A list of Node objects
NODES = []

def fancyname_has_suffix(fancyname, suffix):
    ns = fancyname.split(":")
    if len(ns) == 1:
        return False
    if len(ns) > 2:
        sys.exit("Invalid node specification: %s => EXIT." % fancyname)
    return ns[1] == suffix

def set_NODES(fancynames_in_one_string):
    fancynames = fancynames_in_one_string.split(' ')
    for fancyname in fancynames:
        if fancyname == "":
            continue
        node_id = fancyname.split(":")[0]
        hostname = node_id.split("-")[0]
        os_html = BBSutils.getNodeSpec(hostname, 'OS').replace(' ', '&nbsp;')
        arch = BBSutils.getNodeSpec(hostname, 'Arch')
        platform = BBSutils.getNodeSpec(hostname, 'Platform')
        foreign = fancyname_has_suffix(fancyname, "foreign")
        if foreign:
            buildbin = pkgs = None
        else:
            buildbin = fancyname_has_suffix(fancyname, "bin")
            pkgType = BBSutils.getNodeSpec(hostname, 'pkgType')
            pkgs = bbs.parse.get_meat_packages_for_node(
                                               BBSutils.meat_index_file,
                                               hostname, arch, pkgType)
        node = Node(hostname, node_id, os_html, arch, platform, buildbin, pkgs)
        NODES.append(node)
    if len(NODES) == 0:
        sys.exit("nothing to report (no nodes) => EXIT.")
    return

def is_doing_buildbin(node):
    return node.buildbin == True  # node.buildbin can be None if foreign node

def supported_pkgs(node):
    return node.pkgs

def is_supported(pkg, node):
    return pkg in supported_pkgs(node)

def supported_nodes(pkg):
    nodes = []
    for node in NODES:
        if node.buildbin == None:  # foreign node
            continue
        if is_supported(pkg, node):
            nodes.append(node)
    return nodes


##############################################################################
###
### make_report_title()
### stages_to_display()
###
##############################################################################

def make_report_title(report_nodes):
    buildtype = BBSvars.buildtype
    if buildtype == "bioc-longtests":
        title = "Long Tests"
    elif buildtype == "workflows":
        title = "Workflows build"
    elif buildtype == "books":
        title = "Books build"
    elif buildtype == "bioc-mac-arm64":
        title = "Mac ARM64 build"
    else:
        nnodes = 0
        for node in report_nodes.split(' '):
            if node == "":
                continue
            nnodes += 1
        if buildtype == "bioc-testing":
            title = '"Blame Jeroen" build/check'
        elif nnodes != 1:
            title = "Multiple platform build/check"
        else:
            title = "Build/check"
    title += " report for "
    if buildtype == "cran":
        title += "CRAN"
    else:
        title += "BioC %s" % BBSvars.bioc_version
        if buildtype == "data-annotation":
            title += " annotations"
        elif buildtype == "data-experiment":
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
## buildtype. Should be a subset of the stages that were run because we
## obviously can't display the results for stages that we didn't run.
## However we don't necessarily want to display the results for all the
## stages that we ran. For example, for the "bioc-longtests" buildtype
## we run 'buildsrc' (STAGE3) and 'checksrc' (STAGE4) but we only display
## the results of 'checksrc' (CHECK column on the report).
def stages_to_display(buildtype):
    if buildtype in ["data-annotation", "data-experiment", "books"]:
        return ['install', 'buildsrc', 'checksrc']
    if buildtype == "workflows":
        return ['install', 'buildsrc']
    if buildtype == "bioc-longtests":
        return ['checksrc']  # we run 'buildsrc' but don't display it
    return ['install', 'buildsrc', 'checksrc', 'buildbin']

### Whether to display the package propagation status led or not for the
### given buildtype.
def display_propagation_status(buildtype):
    return buildtype not in ["bioc-longtests", "bioc-testing", "cran"]

def ncol_to_display(buildtype):
    return len(stages_to_display(buildtype)) + \
           display_propagation_status(buildtype)


##############################################################################

BUILD_STATUS_DB_file = 'BUILD_STATUS_DB.txt'
PROPAGATION_STATUS_DB_file = 'PROPAGATION_STATUS_DB.txt'


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
    if rawmap == None:
        return None
    segs = rawmap.split(" ")
    for seg in segs:
        pkgtype, rest = seg.split(":")
        anode = rest.split("/")[0]
        map[anode] = pkgtype
    if not node in map:
        return None
    return map[node]

def get_status(dcf, pkg, node_id, stage):
    key = '%s#%s#%s' % (pkg, node_id, stage)
    status = bbs.parse.get_next_DCF_val(dcf, key, full_line=True)
    return status

def get_propagation_status_from_db(pkg, node_id):
    try:
        dcf = open(PROPAGATION_STATUS_DB_file, 'rb')
    except FileNotFoundError:
        return None
    status = get_status(dcf, pkg,
                        map_outgoing_node_to_package_type(node_id),
                        'propagate')
    dcf.close()
    return status

def WReadDcfVal(rdir, file, field, full_line=False):
    dcf = rdir.WOpen(file)
    val = bbs.parse.get_next_DCF_val(dcf, field, full_line)
    dcf.close()
    return val

### Get vcs metadata for Rpacks/ or Rpacks/pkg/
def get_vcs_meta(pkg, key):
    Central_rdir = BBSvars.Central_rdir
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
### import_BUILD_STATUS_DB()
### get_pkg_status()
###
##############################################################################

def _get_pkg_status_from_BUILD_STATUS_DB(BUILD_STATUS_DB, pkg, node_id, stage):
    key = '%s#%s#%s' % (pkg, node_id, stage)
    return BUILD_STATUS_DB[key]

_build_status_db = {}

def _set_pkg_status(pkg, node_id, stage, status):
    if pkg not in _build_status_db:
        _build_status_db[pkg] = {}
    if node_id not in _build_status_db[pkg]:
        _build_status_db[pkg][node_id] = {}
    _build_status_db[pkg][node_id][stage] = status
    return

def _zero_quickstats():
    quickstats = {}
    for node in NODES:
        if node.buildbin == None:  # foreign node
            continue
        quickstats[node.node_id] = { 'install':     (0, 0, 0, 0, 0), \
                                     'buildsrc':    (0, 0, 0, 0, 0), \
                                     'checksrc':    (0, 0, 0, 0, 0), \
                                     'buildbin':    (0, 0, 0, 0, 0) }
    return quickstats

def _update_quickstats(quickstats, node_id, stage, status):
    x = quickstats[node_id][stage]
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
    quickstats[node_id][stage] = (x0, x1, x2, x3, x4)
    return

def import_BUILD_STATUS_DB(allpkgs):
    BUILD_STATUS_DB = bbs.parse.parse_DCF(BUILD_STATUS_DB_file,
                                          merge_records=True)
    allpkgs_quickstats = _zero_quickstats()
    for pkg in allpkgs:
        for node in supported_nodes(pkg):
            # INSTALL status
            if BBSvars.buildtype != "bioc-longtests":
                stage = 'install'
                status = _get_pkg_status_from_BUILD_STATUS_DB(
                                  BUILD_STATUS_DB,
                                  pkg, node.node_id, stage)
                _set_pkg_status(pkg, node.node_id, stage, status)
                _update_quickstats(allpkgs_quickstats,
                                   node.node_id, stage, status)
            # BUILD status
            stage = 'buildsrc'
            status = _get_pkg_status_from_BUILD_STATUS_DB(
                              BUILD_STATUS_DB,
                              pkg, node.node_id, stage)
            _set_pkg_status(pkg, node.node_id, stage, status)
            _update_quickstats(allpkgs_quickstats, node.node_id, stage, status)
            skipped_is_OK = status in ["TIMEOUT", "ERROR"]
            # CHECK status
            if BBSvars.buildtype != "workflows":
                stage = 'checksrc'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = _get_pkg_status_from_BUILD_STATUS_DB(
                                      BUILD_STATUS_DB,
                                      pkg, node.node_id, stage)
                _set_pkg_status(pkg, node.node_id, stage, status)
                _update_quickstats(allpkgs_quickstats,
                                   node.node_id, stage, status)
            # BUILD BIN status
            if is_doing_buildbin(node):
                stage = 'buildbin'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = _get_pkg_status_from_BUILD_STATUS_DB(
                                      BUILD_STATUS_DB,
                                      pkg, node.node_id, stage)
                _set_pkg_status(pkg, node.node_id, stage, status)
                _update_quickstats(allpkgs_quickstats,
                                   node.node_id, stage, status)
    return allpkgs_quickstats

def get_pkg_status(pkg, node_id, stage):
    if len(_build_status_db) == 0:
        sys.exit("You must import package statuses with " + \
                 "BBSreportutils.import_BUILD_STATUS_DB() before " + \
                 "using BBSreportutils.get_pkg_status() => EXIT.")
    return _build_status_db[pkg][node_id][stage]

def get_distinct_pkg_statuses(pkg, nodes=None):
    if nodes == None:
        nodes = NODES
    statuses = []
    for node in nodes:
        if node.buildbin == None:  # foreign node
            continue
        if not is_supported(pkg, node):
            continue
        stages = stages_to_display(BBSvars.buildtype)
        if 'buildbin' in stages and not is_doing_buildbin(node):
            stages.remove('buildbin')
        for stage in stages:
            status = get_pkg_status(pkg, node.node_id, stage)
            if status != "skipped" and status not in statuses:
                statuses.append(status)
    return statuses


##############################################################################
### Used in mini reports for direct reverse deps
##############################################################################

### Only report reverse deps that are **within** 'pkgs'.
def get_inner_reverse_deps(pkgs, pkg_dep_graph):
    inner_rev_deps = {}
    for pkg in pkgs:
        inner_rev_deps[pkg] = []
    for pkg in pkg_dep_graph.keys():
        if pkg not in pkgs:
            continue
        pkg_direct_deps = pkg_dep_graph[pkg]
        for pkg_direct_dep in pkg_direct_deps:
            if pkg_direct_dep not in pkgs or \
               pkg in inner_rev_deps[pkg_direct_dep]:
                continue
            inner_rev_deps[pkg_direct_dep].append(pkg)
    for pkg in pkgs:
        inner_rev_deps[pkg].sort(key=str.lower)
    return inner_rev_deps

def compute_quickstats(pkgs):
    quickstats = _zero_quickstats()
    for pkg in pkgs:
        for node in supported_nodes(pkg):
            # INSTALL status
            if BBSvars.buildtype != "bioc-longtests":
                stage = 'install'
                status = get_pkg_status(pkg, node.node_id, stage)
                _update_quickstats(quickstats, node.node_id, stage, status)
            # BUILD status
            stage = 'buildsrc'
            status = get_pkg_status(pkg, node.node_id, stage)
            _update_quickstats(quickstats, node.node_id, stage, status)
            skipped_is_OK = status in ["TIMEOUT", "ERROR"]
            # CHECK status
            if BBSvars.buildtype != "workflows":
                stage = 'checksrc'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = get_pkg_status(pkg, node.node_id, stage)
                _update_quickstats(quickstats, node.node_id, stage, status)
            # BUILD BIN status
            if is_doing_buildbin(node):
                stage = 'buildbin'
                if skipped_is_OK:
                    status = "skipped"
                else:
                    status = get_pkg_status(pkg, node.node_id, stage)
                _update_quickstats(quickstats, node.node_id, stage, status)
    return quickstats

