#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Sep 9, 2020
###
### bbs.parse module
###
### IMPORTANT: The bbs.parse module is imported by the Single Package Builder:
###   https://github.com/Bioconductor/packagebuilder.git
###

import sys
import os
import re
import time
import subprocess


def bytes2str(line):
    if isinstance(line, str):
        return line
    try:
        line = line.decode()  # decode() uses utf-8 encoding by default
    except UnicodeDecodeError:
        line = line.decode("iso8859")  # typical Windows encoding
    return line

def version_is_valid(version_string):
    version_regex = '^[0-9]+([.-][0-9]+)*$'
    p = re.compile(version_regex)
    m = p.match(version_string)
    return m != None

### 'srcpkg_path' must be the path to a package source tarball (.tar.gz file).
def get_pkgname_from_srcpkg_path(srcpkg_path):
    srcpkg_file = os.path.basename(srcpkg_path)
    srcpkg_regex = '^([^_]+)_([^_]+)\\.tar\\.gz$'
    p = re.compile(srcpkg_regex)
    m = p.match(srcpkg_file)
    pkgname = m.group(1)
    return pkgname

### 'srcpkg_path' must be the path to a package source tarball (.tar.gz file).
def get_version_from_srcpkg_path(srcpkg_path):
    srcpkg_file = os.path.basename(srcpkg_path)
    srcpkg_regex = '^([^_]+)_([^_]+)\\.tar\\.gz$'
    p = re.compile(srcpkg_regex)
    m = p.match(srcpkg_file)
    version = m.group(2)
    return version


##############################################################################
### Generic DCF parser
###

class DcfParsingError(Exception):
    def __init__(self, filepath, lineno, msg):
        self.filepath = filepath
        self.lineno = lineno
        self.msg = msg
    def __str__(self):
        return 'in DCF file \'%s\' at line %d:\n  %s' % \
               (self.filepath, self.lineno, self.msg)

### Return a list of DCF records. Each record is represented as a dictionary
### of key-value pairs where the key is a DCF field name and the value a
### string.
def parse_DCF(filepath, merge_records=False):
    f = open(filepath, 'r')
    if merge_records:
        rec1 = {}
    else:
        records = []
    recno = 0
    rec_firstlineno = 0
    lineno = 0
    for line in f:
        lineno += 1
        line2 = line.strip()
        ## The current line is empty.
        if line2 == '':
            if rec_firstlineno != 0:
                if merge_records:
                    rec1.update(rec)
                else:
                    records.append(rec)
                rec_firstlineno = 0
        elif line.startswith('#'):
            continue  # skip comment lines
        elif line.startswith(' ') or line.startswith('\t'):
            if rec_firstlineno == 0:
                msg = 'whitespace unexpected at beginning of line'
                raise DcfParsingError(filepath, lineno, msg)
            ## The current line is the continuation of the latest value.
            val = rec[key]
            rec[key] = line2 if val == '' else val + ' ' + line2
        else:
            pos = line.find(':')
            if pos == -1:
                what = '\':\'' if rec_firstlineno == 0 else 'leading whitespace'
                msg = 'invalid line (%s missing?)' % what
                raise DcfParsingError(filepath, lineno, msg)
            ## The current line is a key-value pair.
            if rec_firstlineno == 0:
                ## The current line is the first key-value pair in the record.
                rec = {}
                recno += 1
                rec_firstlineno = lineno
            key = line[:pos]
            val = line[pos+1:].strip()
            rec[key] = val
    f.close()
    if rec_firstlineno != 0:
        if merge_records:
            rec1.update(rec)
        else:
            records.append(rec)
    return rec1 if merge_records else records


##############################################################################
### Other DCF parsing utilities
###

class DcfFieldNotFoundError(Exception):
    def __init__(self, filepath, field):
        self.filepath = filepath
        self.field = field
    def __str__(self):
        return "Field '%s' not found in DCF file '%s'" % \
               (self.field, self.filepath)

### Get the next field/value pair from a DCF file.
### The field value starts at the first non-whitespace character following
### the ":". Where it ends depends on the value of the full_line arg:
###   - if full_line is True: it ends at the end of the line,
###   - if full_line is False: it ends at the first whitespace following
###     the start of the value.
###   - if the value is empty, return ""
def get_next_DCF_fieldval(dcf, full_line=False):
    if full_line:
        val_regex = '\\S.*'
    else:
        val_regex = '\\S+'
    regex = '([A-Za-z0-9_.-]+)\\s*:\\s*(%s)' % val_regex
    p = re.compile(regex)
    for line in dcf:
        line = bytes2str(line)
        m = p.match(line)
        if m:
            field = m.group(1)
            val = m.group(2)
            return (field, val)
    return None

### Get the next value of the field specified by the user from a DCF file.
def get_next_DCF_val(dcf, field, full_line=False):
    if full_line:
        val_regex = '\\S.*'
    else:
        val_regex = '\\S+'
    regex = '%s\\s*:\\s*(%s)' % (field, val_regex)
    p = re.compile(regex)
    for line in dcf:
        line = bytes2str(line)
        if not line.startswith(field + ":"):
            continue
        m = p.match(line)
        if m:
            val = m.group(1)
        else:
            val = ""
        return val
    return None


##############################################################################
### Parse a DESCRIPTION file
###

def get_DESCRIPTION_path(pkgsrctree):
    return os.path.join(pkgsrctree, 'DESCRIPTION')

def get_Package_from_pkgsrctree(pkgsrctree):
    desc_file = get_DESCRIPTION_path(pkgsrctree)
    dcf = open(desc_file, 'rb')
    pkg = get_next_DCF_val(dcf, 'Package')
    dcf.close()
    if pkg == None:
        raise DcfFieldNotFoundError(desc_file, 'Package')
    return pkg

def get_Version_from_pkgsrctree(pkgsrctree):
    desc_file = get_DESCRIPTION_path(pkgsrctree)
    dcf = open(desc_file, 'rb')
    version = get_next_DCF_val(dcf, 'Version')
    dcf.close()
    if version == None:
        raise DcfFieldNotFoundError(desc_file, 'Version')
    return version

### Return the name of the package source tarball that would result
### from building the package found at 'pkgsrctree'.
def make_srcpkg_file_from_pkgsrctree(pkgsrctree):
    pkgname = get_Package_from_pkgsrctree(pkgsrctree)
    version = get_Version_from_pkgsrctree(pkgsrctree)
    srcpkg_file = '%s_%s.tar.gz' % (pkgname, version)
    return srcpkg_file

def get_PackageStatus_pkgsrctree(pkgsrctree):
    desc_file = get_DESCRIPTION_path(pkgsrctree)
    dcf = open(desc_file, 'rb')
    version = get_next_DCF_val(dcf, 'PackageStatus')
    dcf.close()
    if version == None:
        return "OK"
    return version

def get_Maintainer_from_pkgsrctree(pkgsrctree):
    r_home = os.environ['BBS_R_HOME']
    BBS_home = os.environ['BBS_HOME']
    desc_file = get_DESCRIPTION_path(pkgsrctree)
    FNULL = open(os.devnull, 'w')
    Rscript_cmd = os.path.join(r_home, "bin", "Rscript")
    script_path = os.path.join(BBS_home, "utils", "getMaintainer.R")
    cmd = [Rscript_cmd, '--vanilla', script_path, desc_file]
    maintainer = bytes2str(subprocess.check_output(cmd, stderr=FNULL))
    if maintainer == 'NA':
        raise DcfFieldNotFoundError(desc_file, 'Maintainer')
    return maintainer

def get_Maintainer_name_from_pkgsrctree(pkgsrctree):
    maintainer = get_Maintainer_from_pkgsrctree(pkgsrctree)
    regex = '(.*\S)\s*<(.*)>\s*'
    p = re.compile(regex)
    m = p.match(maintainer)
    if m:
        maintainer = m.group(1)
    return maintainer

def get_Maintainer_email_from_pkgsrctree(pkgsrctree):
    maintainer = get_Maintainer_from_pkgsrctree(pkgsrctree)
    regex = '(.*\S)\s*<(.*)>\s*'
    p = re.compile(regex)
    m = p.match(maintainer)
    if m:
        email = m.group(2)
    else:
        DESCRIPTION_path = get_DESCRIPTION_path(pkgsrctree)
        raise DcfFieldNotFoundError(DESCRIPTION_path, 'Maintainer email')
    return email


##############################################################################
### Extract options from a package .BBSoptions file
###

def get_BBSoption_from_pkgsrctree(pkgsrctree, key):
    option_file = os.path.join(pkgsrctree, '.BBSoptions')
    try:
        dcf = open(option_file, 'rb')
        val = get_next_DCF_val(dcf, key, True)
        dcf.close()
    except IOError:
        val = None
    return val


##############################################################################
### Extract specific fields from a package index in DCF format
###

def getPkgFieldFromDCF(dcf, pkg, field, data_desc):
    pkg2 = ""
    while pkg2 != pkg:
        pkg2 = get_next_DCF_val(dcf, 'Package', False)
        if pkg2 == None:
            print("ERROR: Can't find package '%s' in DCF file '%s'!" % (pkg, data_desc))
            raise DcfFieldNotFoundError(data_desc, 'Package')
    val = get_next_DCF_val(dcf, field, True)
    if val == None:
        print("ERROR: Can't find field '%s' for package '%s' in DCF file '%s'!" % (field, pkg, data_desc))
        raise DcfFieldNotFoundError(data_desc, field)
    return val

### 'node_id' is the name of the node and 'pkgType' the native package type for
### this node ("source", "win.binary", "win64.binary", "mac.binary",
### "mac.binary.mavericks", or "mac.binary.el-capitan").
def readPkgsFromDCF(dcf, node_id=None, pkgType=None):
    pkgs = []
    while True:
        pkg = get_next_DCF_val(dcf, 'Package')
        if not pkg:
            break
        supported = True
        if node_id or pkgType:
            unsupported = get_next_DCF_val(dcf, 'UnsupportedPlatforms', True)
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

### Inject fields into DESCRIPTION
def injectFieldsInDESCRIPTION(desc_file, gitlog_file):
    # git-log
    dcf = open(gitlog_file, 'rb')
    git_url = get_next_DCF_val(dcf, 'URL')
    git_branch = get_next_DCF_val(dcf, 'Branch')
    git_last_commit = get_next_DCF_val(dcf, 'Last Commit')
    git_last_commit_date = get_next_DCF_val(dcf, 'Last Changed Date')
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
    # Handle the following cases:
    # - no EOL character at the end of the last line 
    # - blank line at the end of the file
    target_keys = ['git_url', 'git_branch', 'git_last_commit',
                   'git_last_commit_date', 'Date/Publication']
    dcf = open(desc_file, 'rb')
    lines = dcf.read().splitlines()
    dcf.close()
    dcf = open(desc_file, 'wb')
    p = re.compile(':|'.join(target_keys) + ':')
    for line in lines:
        s = bytes2str(line)
        if not s.strip():  # drop empty lines
            continue
        if not p.match(s):
            dcf.write(line + b'\n')
    dcf.close()

    # Note that we open the DESCRIPTION file for appending using the utf-8
    # encoding (well, we don't know the original encoding of the file) so
    # the lines we append to it will be encoded using an encoding that will
    # not necessarily match the original encoding of the file. However, the
    # strings we actually append only contain ASCII code so hopefully they
    # get encoded the same way as if we had used the original encoding of
    # the file.
    dcf = open(desc_file, 'a', encoding="utf-8")
    dcf.write('%s: %s\n' % (target_keys[0], git_url))
    dcf.write('%s: %s\n' % (target_keys[1], git_branch))
    dcf.write('%s: %s\n' % (target_keys[2], git_last_commit))
    dcf.write('%s: %s\n' % (target_keys[3], git_last_commit_date))
    dcf.write('%s: %s\n' % (target_keys[4], time.strftime("%Y-%m-%d")))
    dcf.close()


##############################################################################
### Some utilities for parsing the tail of install.packages(), 'R CMD build',
### and 'R CMD check' output.
###

def readFileTail(filename, n):
    last_lines = n * [None]
    f = open(filename, 'rb')
    nb_lines = i = 0
    for line in f:
        line = bytes2str(line)
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

### Assume 'out_file' is a file containing the output of 'R CMD INSTALL' or
### 'install.packages()'.
### Only parse the last 12 lines of the output file.
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

### Assume 'out_file' is a file containing the output of install.packages().
### Extract the name of the locking package from the last 12 lines of the output
### file.
def extractLockingPackage(out_file):
    tail = readFileTail(out_file, 12)
    regex = r'^Try removing .*/00LOCK-([\w\.]*)'
    p = re.compile(regex)
    for line in tail:
        m = p.match(line)
        if m != None:
            return m.group(1)
    return None

### Assume 'out_file' is a file containing the output of 'R CMD check'.
### Only parse the last 6 lines of the output file.
### Return a string!
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

