##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: May 31, 2023
###
### IMPORTANT: The BBSutils.py file is imported by the Single Package Builder:
###   https://github.com/Bioconductor/packagebuilder.git
###

import sys
import os
import shutil
#import urllib.request
import hashlib
import logging

import bbs.fileutils
import bbs.jobs
import bbs.rdir

logging.basicConfig(format='%(levelname)s: %(asctime)s %(filename)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG)

# TODO: Indent the output (use length of stack as the indent level)
class Debug:
    def __init__(self, ps='BBS:debug> '):
        self.is_on = False
        self.ps = ps
        self.stack = []
    def Print(self, msg):
        if not self.is_on:
            return
        print("%s%s" % (self.ps, msg))
        sys.stdout.flush()
        return
    def Begin(self, f, args=[]):
        if not self.is_on:
            return
        self.stack.append(f)
        fargs = f + '('
        is_first = True
        for arg in args:
            if not is_first:
                fargs += ', '
            fargs += str(arg)
            is_first = False
        fargs += ')'
        self.Print('BEGIN %s' % fargs)
        return
    def End(self):
        if not self.is_on:
            return
        f = self.stack.pop()
        self.Print('END of %s' % f)
        return

debug = Debug()

def getenv(name, is_required=True, default=None):
    if name in os.environ and os.environ[name] != "":
        val = os.environ[name]
    elif is_required:
        print("BBSutils ERROR: Environment variable %s" % name, end=" ")
        if not name in os.environ:
            print("not found!")
        else:
            print("is an empty string!")
        sys.exit("==> EXIT")
    else:
        val = default
    debug.Print("%s=%s" % (name, val))
    return val

debug.is_on = int(getenv('BBS_DEBUG', False, "0")) != 0



##############################################################################
### GLOBAL CONSTANTS
##############################################################################

meat_index_file = 'meat-index.dcf'
skipped_index_file = 'skipped-index.dcf'
pkg_dep_graph_file = 'pkg_dep_graph.txt'

#sys.path.append(os.path.join(BBS_home, "nodes"))
import nodes.nodespecs

pkgType2FileExt = {
    'source': "tar.gz",
    'win.binary': "zip",
    'win64.binary': "zip",
    'mac.binary': "tgz",
    'mac.binary.big-sur-x86_64': "tgz",
    'mac.binary.big-sur-arm64': "tgz",
    'mac.binary.leopard': "tgz",
    'mac.binary.mavericks': "tgz",
    'mac.binary.el-capitan': "tgz"
}

def getNodeSpec(node_hostname, key, key_is_optional=False):
    specs = nodes.nodespecs.allnodes[node_hostname.lower()]
    if key == 'pkgFileExt':
        return pkgType2FileExt[specs['pkgType']]
    if key_is_optional:
        return specs.get(key)
    return specs[key]


##############################################################################
### copyTheDamnedThingNoMatterWhat()
##############################################################################

### Copying stuff locally can be a **real** challenge on Windows!
### It can fail for various reasons e.g. a process holding on the file to
### copy, or the file path is too long.
###
### Example: shutil.copy2() will fail on Windows if a process is sill holding
### on the file to copy. Similarly shutil.copytree() will fail if a process
### is still holding on a file located inside the directory to copy, or if the
### directory contains files with paths that are too long. The first situation
### has been observed when calling shutil.copytree() on 'NetSAM.Rcheck' on a
### Windows build machine right after 'R CMD check' failed. Note that the
### latter failed with:
###   ..
###   * checking files in 'vignettes' ... OK
###   * checking examples ... ERROR
###   Running examples in 'NetSAM-Ex.R' failed
###   Warning in file(con, "r") :
###     cannot open file 'NetSAM-Ex.Rout': Permission denied
###   Error in file(con, "r") : cannot open the connection
###   Execution halted
###
### So it failed exactly for the very reason that a process was holding on
### 'NetSAM.Rcheck\NetSAM-Ex.Rout' hence preventing 'R CMD check' from opening
### the file to parse its content for errors.
###
### Then, when almost immediately after that, BBS tried to copy 'NetSAM.Rcheck'
### with shutil.copytree(), it failed with:
###
###   [Errno 13] Permission denied: 'NetSAM.Rcheck\NetSAM-Ex.Rout'
###
### because the process holding on 'NetSAM.Rcheck\NetSAM-Ex.Rout' was still
### there!
### The magic bullet is to use rsync to copy stuff locally. Sounds overkill
### but it seems to work no matter what.

def copyTheDamnedThingNoMatterWhat(src, destdir):
    bbs.rdir.set_readable_flag(src)
    if sys.platform == 'win32':
        ## rsync should do it no matter what.
        rsync_cmd = getenv('BBS_RSYNC_CMD')
        src = bbs.fileutils.to_cygwin_style(src)
        destdir = bbs.fileutils.to_cygwin_style(destdir)
        cmd = '%s -rL %s %s' % (rsync_cmd, src, destdir)
        ## Looks like rsync can sometimes have hiccups on Windows where it
        ## gets stuck forever (timeout) even when trying to perform a local
        ## copy. So we need to try harder (up to 3 attemps before we give up).
        #bbs.jobs.runJob(cmd, stdout=None, maxtime=120.0, verbose=True)
        bbs.jobs.tryHardToRunJob(cmd, nb_attempts=3, stdout=None,
                                 maxtime=60.0, sleeptime=10.0,
                                 failure_is_fatal=False, verbose=True)
    else:
        print("BBS>   Copying %s to %s/ ..." % (src, destdir), end=" ")
        sys.stdout.flush()
        if os.path.isdir(src):
            dst = os.path.join(destdir, os.path.basename(src))
            if os.path.exists(dst):
                bbs.fileutils.nuke_tree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, destdir)
        print("OK")
        sys.stdout.flush()
    return


##############################################################################
### downloadFile()
##############################################################################

### From https://stackoverflow.com/questions/3431825/
def _md5(file):
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def downloadFile(file, baseurl, destdir, MD5sum=None, timeout=600):
    print('downloading %s' % file, end=' ')
    sys.stdout.flush()
    url = baseurl + '/' + file
    destfile = os.path.join(destdir, file)
    if MD5sum != None and os.path.exists(destfile):
        current = _md5(destfile)
        if current == MD5sum:
            print('--> skip (identical to local)')
            return
    print('...', end=' ')
    sys.stdout.flush()
    #urllib.request.urlretrieve(url, destfile)
    ## An alternative to urllib.request.urlretrieve() above (from
    ## https://stackoverflow.com/questions/7243750/).
    ## Unlike urllib.request.urlretrieve(), this allows us to control
    ## the timeout limit.
    #response = urllib.request.urlopen(url, timeout=timeout)
    #f = open(destfile, 'wb')
    #shutil.copyfileobj(response, f)
    #f.close()
    ## Unfortunately the urllib.request-based solutions above turn out to
    ## very unreliable, timing out all the time for mysterious reasons.
    ## So we just use good ol' curl command for the download.
    curl_cmd = getenv('BBS_CURL_CMD')
    cmd = '%s --silent %s --output %s' % (curl_cmd, url, destfile)
    bbs.jobs.tryHardToRunJob(cmd, nb_attempts=3, maxtime=timeout, sleeptime=5.0)
    if MD5sum != None:
        current = _md5(destfile)
        #print('(%s)' % current, end=' ')
        #sys.stdout.flush()
        assert current == MD5sum
    print('ok')
    return destfile

