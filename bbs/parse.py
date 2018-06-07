#!/usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: June 7, 2018
###
### parse module
###

import os
import re
import subprocess
import BBScorevars
from bbs.dcf.dcfrecordsparser import DcfRecordParser

class DcfFieldNotFoundError(Exception):
    def __init__(self, file, field):
        self.file = file
        self.field = field
    def __str__(self):
        return "\n  Can't extract '%s' from DCF file '%s'\n  Is the file readable?" % (self.field, self.file)

# Get the next field/value pair from a DCF file.
# The field value starts at the first non-whitespace character following
# the ":". Where it ends depends on the value of the full_line arg:
#   - if full_line is True: it ends at the end of the line,
#   - if full_line is False: it ends at the first whitespace following
#     the start of the value.
#   - if the value is empty, return ""
def getNextDcfFieldVal(dcf, full_line=False):
    if full_line:
        val_regex = '\\S.*'
    else:
        val_regex = '\\S+'
    regex = '([A-Za-z0-9_.-]+)\\s*:\\s*(%s)' % val_regex
    p = re.compile(regex)
    for line in dcf:
        m = p.match(line)
        if m:
            field = m.group(1)
            val = m.group(2)
            return (field, val)
    return None

# Get the next value of the field specified by the user from a DCF file.
def getNextDcfVal(dcf, field, full_line=False):
    if full_line:
        val_regex = '\\S.*'
    else:
        val_regex = '\\S+'
    regex = '%s\\s*:\\s*(%s)' % (field, val_regex)
    p = re.compile(regex)
    val = None
    for line in dcf:
        if not line.startswith(field + ":"):
            continue
        m = p.match(line)
        if m:
            val = m.group(1)
        else:
            val = ""
        break
    return val;

def getDescFile(pkg_dir):
    return os.path.join(pkg_dir, 'DESCRIPTION')

def getPkgFromDir(pkg_dir):
    desc_file = getDescFile(pkg_dir)
    dcf = open(desc_file, 'r')
    pkg = getNextDcfVal(dcf, 'Package')
    dcf.close()
    if pkg == None:
        raise DcfFieldNotFoundError(desc_file, 'Package')
    return pkg

def getVersionFromDir(pkg_dir):
    desc_file = getDescFile(pkg_dir)
    dcf = open(desc_file, 'r')
    version = getNextDcfVal(dcf, 'Version')
    dcf.close()
    if version == None:
        raise DcfFieldNotFoundError(desc_file, 'Version')
    return version

def getPackageStatusFromDir(pkg_dir):
    desc_file = getDescFile(pkg_dir)
    dcf = open(desc_file, 'r')
    version = getNextDcfVal(dcf, 'PackageStatus')
    dcf.close()
    if version == None:
        return "OK"
    return version

def _getMaintainerFromDir(pkg_dir):
    desc_file = getDescFile(pkg_dir)
    FNULL = open(os.devnull, 'w')
    r_home = BBScorevars.getenv('BBS_R_HOME')
    Rscript_cmd = os.path.join(r_home, "bin", "Rscript")
    script_path = os.path.join(BBScorevars.BBS_home, "utils", "getMaintainer.R")
    cmd = [Rscript_cmd, '--vanilla', script_path, desc_file]
    maintainer = subprocess.check_output(cmd, stderr=FNULL)
    if maintainer == 'NA':
        raise DcfFieldNotFoundError(desc_file, 'Maintainer')
    return maintainer

def getMaintainerFromDir(pkg_dir):
    maintainer = _getMaintainerFromDir(pkg_dir)
    regex = '(.*\S)\s*<(.*)>\s*'
    p = re.compile(regex)
    m = p.match(maintainer)
    if m:
        maintainer = m.group(1)
    return maintainer

def getMaintainerEmailFromDir(pkg_dir):
    maintainer = _getMaintainerFromDir(pkg_dir)
    regex = '(.*\S)\s*<(.*)>\s*'
    p = re.compile(regex)
    m = p.match(maintainer)
    if m:
        email = m.group(2)
    else:
        #email = None
        raise DcfFieldNotFoundError(getDescFile(pkg_dir), 'Maintainer email')
    return email

def getBBSoptionFromDir(pkg_dir, key):
    try:
        option_file = os.path.join(pkg_dir, '.BBSoptions')
        dcf = open(option_file, 'r')
        val = getNextDcfVal(dcf, key, True)
        dcf.close()
    except IOError:
        val = None
    return val

def getPkgFieldFromDCF(dcf, pkg, field, data_desc):
    pkg2 = ""
    while pkg2 != pkg:
        pkg2 = getNextDcfVal(dcf, 'Package', False)
        if pkg2 == None:
            print "ERROR: Can't find package '%s' in DCF file '%s'!" % (pkg, data_desc)
            raise DcfFieldNotFoundError(data_desc, 'Package')
    val = getNextDcfVal(dcf, field, True)
    if val == None:
        print "ERROR: Can't find field '%s' for package '%s' in DCF file '%s'!" % (field, pkg, data_desc)
        raise DcfFieldNotFoundError(data_desc, field)
    return val

### 'node_id' is the name of the node and 'pkgType' the native package type for
### this node ("source", "win.binary", "win64.binary", "mac.binary",
### "mac.binary.mavericks", or "mac.binary.el-capitan").
def readPkgsFromDCF(dcf, node_id=None, pkgType=None):
    pkgs = []
    while True:
        pkg = getNextDcfVal(dcf, 'Package')
        if not pkg:
            break
        supported = True
        if node_id or pkgType:
            unsupported = getNextDcfVal(dcf, 'UnsupportedPlatforms', True)
            for x in unsupported.split(","):
                x = x.strip()
                if x in ["", "None", "NA"]:
                    continue
                if node_id and x == node_id:
                    supported = False
                    break
                if not pkgType or pkgType == "source":
                    continue
                # if 'x' is mac.binary or mac.binary.*
                if pkgType and x == pkgType:
                    supported = False
                    break
                # if 'x' is win or mac and pkgType is win.binary or mac.*:
                if x in ["win", "mac"]:
                    if pkgType.startswith(x):
                        supported = False
                        break
        if supported:
            pkgs.append(pkg)
    return pkgs

# Return the name of the srcpkg file that would result
# from building the pkg found at pkg_dir.
def getSrcPkgFileFromDir(pkg_dir):
    pkg = getPkgFromDir(pkg_dir)
    version = getVersionFromDir(pkg_dir)
    srcpkg_file = pkg + '_' + version + '.tar.gz'
    return srcpkg_file

# srcpkg_path must be a path to a package source tarball (.tar.gz file).
def getPkgFromPath(srcpkg_path):
    srcpkg_file = os.path.basename(srcpkg_path)
    srcpkg_regex = '^([^_]+)_([^_]+)\\.tar\\.gz$'
    p = re.compile(srcpkg_regex)
    m = p.match(srcpkg_file)
    pkg = m.group(1)
    return pkg

# srcpkg_path must be a path to a srcpkg file (.tar.gz file).
def getVersionFromPath(srcpkg_path):
    srcpkg_file = os.path.basename(srcpkg_path)
    srcpkg_regex = '^([^_]+)_([^_]+)\\.tar\\.gz$'
    p = re.compile(srcpkg_regex)
    m = p.match(srcpkg_file)
    version = m.group(2)
    return version

# Inject fields into DESCRIPTION
def injectFieldsInDESCRIPTION(desc_file, gitlog_file):
    # git-log
    dcf = open(gitlog_file, 'r')
    git_url = getNextDcfVal(dcf, 'URL')
    git_branch = getNextDcfVal(dcf, 'Branch')
    git_last_commit = getNextDcfVal(dcf, 'Last Commit')
    git_last_commit_date = getNextDcfVal(dcf, 'Last Changed Date')
    dcf.close()
    if git_url == None:
        raise DcfFieldNotFoundError(gitlog_file, 'URL')
    if git_branch == None:
        raise DcfFieldNotFoundError(gitlog_file, 'Branch')
    if git_last_commit == None:
        raise DcfFieldNotFoundError(gitlog_file, 'Last Commit')
    if git_last_commit_date == None:
        raise DcfFieldNotFoundError(gitlog_file, 'Last Changed Date')

    # DESCRIPTION
    # Not all DESCRIPTION files have a newline at the end of the last 
    # line. This results in a mangled append of the 'git' fields. To avoid 
    # this, we strip newlines when reading the file and explicitly write a
    # newline to each row.
    dcf = open(desc_file, 'r')
    lines = dcf.read().splitlines()
    dcf.close()
    dcf = open(desc_file, 'w')
    p = re.compile('git_url|git_branch|git_last_commit|git_last_commit_date')
    for line in lines:
        if not p.match(line):
            dcf.write(line + '\n')
    dcf.close()

    dcf = open(desc_file, 'a')
    dcf.write("git_url: %s\n" % git_url)
    dcf.write("git_branch: %s\n" % git_branch)
    dcf.write("git_last_commit: %s\n" % git_last_commit)
    dcf.write("git_last_commit_date: %s\n" % git_last_commit_date)
    dcf.close()

##############################################################################
# Some utilities for parsing the tail of install.packages(), 'R CMD build',
# and 'R CMD check' output.
#

def readFileTail(filename, n):
    last_lines = n * [None]
    f = open(filename, 'r')
    nb_lines = i = 0
    for line in f:
        nb_lines += 1
        if n != 0:
            last_lines[i] = line
            i += 1
            if i >= n:
                i = 0
    f.close()
    if nb_lines < n:
        n2 = nb_lines
        i = 0
    else:
        n2 = n
    tail = n2 * [None]
    for j in range(n2):
        tail[j] = last_lines[i]
        i += 1
        if i >= n:
            i = 0
    return tail

# Assume 'out_file' is a file containing the output of 'R CMD INSTALL' or
# 'install.packages()'.
# Only parse the last 12 lines of the output file.
def installPkgWasOK(out_file, pkg):
    tail = readFileTail(out_file, 12)
    # We're looking for bad news instead of good news. That's because there is
    # nothing that indicates success in the output of 'install.packages()' when
    # installing a binary package on Mac.
    #regex1 = r'^\* DONE \(%s\)' % pkg
    #regex2 = r'^package \'%s\' successfully unpacked and MD5 sums checked' % pkg
    regex1 = r'^\* removing'
    regex2 = r'installation of package .* had non-zero exit status'
    regex3 = r'Error in install\.packages\("%s"' % pkg
    p1 = re.compile(regex1)
    p2 = re.compile(regex2)
    p3 = re.compile(regex3)
    for line in tail:
        m = p1.match(line)
        if m != None:
            return False
        m = p2.match(line)
        if m != None:
            return False
        m = p3.match(line)
        if m != None:
            return False
    return True

# Assume 'out_file' is a file containing the output of install.packages().
# Extract the name of the locking package from the last 12 lines of the output
# file.
def extractLockingPackage(out_file):
    tail = readFileTail(out_file, 12)
    regex = r'^Try removing .*/00LOCK-([\w\.]*)'
    p = re.compile(regex)
    for line in tail:
        m = p.match(line)
        if m != None:
            return m.group(1)
    return None

# Assume 'out_file' is a file containing the output of 'R CMD check'.
# Only parse the last 6 lines of the output file.
# Return a string!
def countWARNINGs(out_file):
    tail = readFileTail(out_file, 6)
    regex = '^WARNING: There (was|were) (\\d+) (warning|warnings)|^Status: (\\d+) WARNING'
    p = re.compile(regex)
    for line in tail:
        m = p.match(line)
        if m != None:
            if m.group(4) != None:
                return m.group(4)
            return m.group(2)
    return "0"


if __name__ == "__main__":
    sys.exit("ERROR: this Python module can't be used as a standalone script yet")

