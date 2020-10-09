##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Oct 6, 2020
###
### IMPORTANT: The BBSutils.py file is imported by the Single Package Builder:
###   https://github.com/Bioconductor/packagebuilder.git
###

import sys
import os
import logging

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

#sys.path.append(os.path.join(BBS_home, "nodes"))
import nodes.nodespecs

pkgType2FileExt = {
    'source': "tar.gz",
    'win.binary': "zip",
    'win64.binary': "zip",
    'mac.binary': "tgz",
    'mac.binary.leopard': "tgz",
    'mac.binary.mavericks': "tgz",
    'mac.binary.el-capitan': "tgz"
}

def getNodeSpec(node_hostname, key):
    spec = nodes.nodespecs.allnodes[node_hostname.lower()]
    if key == 'OS':
        return spec[0]
    if key == 'Arch':
        return spec[1]
    if key == 'Platform':
        return spec[2]
    if key == 'pkgType':
        return spec[3]
    if key == 'encoding':
        return spec[4]
    if key == 'pkgFileExt':
        return pkgType2FileExt[spec[3]]
    sys.exit("ERROR: Invalid key '%s'" % key)

