##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: June 30, 2010
###

import sys
import os

import bbs.rdir


# TODO: Indent the output (use length of stack as the indent level)
class Debug:
    def __init__(self, ps='BBS:debug> '):
        self.is_on = False
        self.ps = ps
        self.stack = []
    def Print(self, msg):
        if not self.is_on:
            return
        print "%s%s" % (self.ps, msg)
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
        print "BBScorevars ERROR: Environment variable %s" % name,
        if not name in os.environ:
            print "not found!"
        else:
            print "is an empty string!"
        sys.exit("==> EXIT")
    else:
        val = default
    debug.Print("%s=%s" % (name, val))
    return val

debug.is_on = int(getenv('BBS_DEBUG', False, "0")) != 0

### Just a safety check. Global var 'user' is actually not used.
if sys.platform == "win32":
    running_user = getenv('USERNAME')
else:
    running_user = getenv('USER')
user = getenv('BBS_USER', False, running_user)
if user != running_user:
    print "BBScorevars ERROR: BBS running as user '%s', '%s' expected!" % (running_user, user)
    sys.exit("==> EXIT")



##############################################################################
### BBS CORE GLOBAL VARIABLES
##############################################################################


BBS_home = getenv('BBS_HOME')

sys.path.append(os.path.join(BBS_home, "nodes"))
import nodespecs

pkgType2FileExt = { \
    'source': "tar.gz", \
    'win.binary': "zip", \
    'win64.binary': "zip", \
    'mac.binary': "tgz", \
    'mac.binary.leopard': "tgz", \
    'mac.binary.mavericks': "tgz"
}

def getNodeSpec(node_hostname, key):
    spec = nodespecs.allnodes[node_hostname.lower()]
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

ssh_cmd = getenv('BBS_SSH_CMD', False)
rsync_cmd = getenv('BBS_RSYNC_CMD')
rsync_rsh_cmd = getenv('BBS_RSYNC_RSH_CMD')

central_rdir_path = getenv('BBS_CENTRAL_RDIR', False)
if central_rdir_path == None:
    Central_rdir = bbs.rdir.RemoteDir('BBS_CENTRAL_BASEURL',
                    getenv('BBS_CENTRAL_BASEURL'),
                    None,
                    None,
                    None,
                    None, None, None)
else:
    central_rhost = getenv('BBS_CENTRAL_RHOST', False)
    central_ruser = getenv('BBS_CENTRAL_RUSER', False)
    Central_rdir = bbs.rdir.RemoteDir('BBS_CENTRAL_BASEURL',
                    getenv('BBS_CENTRAL_BASEURL'),
                    central_rdir_path,
                    central_rhost,
                    central_ruser,
                    ssh_cmd, rsync_cmd, rsync_rsh_cmd)

nodes_rdir = Central_rdir.subdir('nodes')

mode = getenv('BBS_MODE', False, "bioc")

r_cmd_timeout = float(getenv('BBS_R_CMD_TIMEOUT', False, "2400.0"))

meat_index_file = 'meat-index.txt'

