##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: May 13, 2011
###

import sys
import os

import bbs.rdir
import bbs.jobs
import BBScorevars


##############################################################################
### BBS GLOBAL VARIABLES
##############################################################################


### Only needed by BBS-prerun.py and BBS-run.py

MEAT0_rdir = bbs.rdir.RemoteDir('BBS_MEAT0_RDIR',
                None,
                BBScorevars.getenv('BBS_MEAT0_RDIR'),
                BBScorevars.getenv('BBS_MEAT0_RHOST', False),
                BBScorevars.getenv('BBS_MEAT0_RUSER', False),
                BBScorevars.ssh_cmd,
                BBScorevars.rsync_cmd,
                BBScorevars.rsync_rsh_cmd)

meat_path = BBScorevars.getenv('BBS_MEAT_PATH')

work_topdir = BBScorevars.getenv('BBS_WORK_TOPDIR')

r_cmd = BBScorevars.getenv('BBS_R_CMD')


### Only needed by BBS-prerun.py

MEAT0_type = int(BBScorevars.getenv('BBS_MEAT0_TYPE'))

update_MEAT0 = int(BBScorevars.getenv('BBS_UPDATE_MEAT0', False, "0")) != 0

if MEAT0_type == 3:
    manifest_file = {'bioc': 'software.txt', 'data-experiment': 'dataexperiment.txt'}[BBScorevars.mode]
    manifest_path = os.path.join(work_topdir, 'manifest', manifest_file)
    git_branch = BBScorevars.getenv('BBS_BIOC_GIT_BRANCH')
else:
    manifest_file = BBScorevars.getenv('BBS_BIOC_MANIFEST_FILE', False)
    manifest_path = os.path.join(MEAT0_rdir.path, manifest_file)

vcsmeta_file = {1: 'svninfo/svn-info.txt', 2: None, 3: 'gitlog/git-log.txt'}[MEAT0_type]
vcsmeta_path = os.path.join(work_topdir, vcsmeta_file)

### Only needed by BBS-run.py

STAGE2_r_script = BBScorevars.getenv('BBS_STAGE2_R_SCRIPT')

hostname0 = bbs.jobs.getHostname()
node_hostname = BBScorevars.getenv('BBS_NODE_HOSTNAME', False, hostname0)
### Check that 'node_hostname' matches the effective hostname:
if node_hostname.lower() != hostname0.lower():
    print "BBSvars ERROR: Found hostname '%s', '%s' expected!" % (hostname0, node_hostname)
    sys.exit("==> EXIT")

node_id = BBScorevars.getenv('BBS_NODE_ID', False, node_hostname)
Node_rdir = BBScorevars.nodes_rdir.subdir(node_id)
install_rdir = Node_rdir.subdir('install')
buildsrc_rdir = Node_rdir.subdir('buildsrc')
checksrc_rdir = Node_rdir.subdir('checksrc')
buildbin_rdir = Node_rdir.subdir('buildbin')

STAGE2_mode = BBScorevars.getenv('BBS_STAGE2_MODE', False)
STAGE4_mode = BBScorevars.getenv('BBS_STAGE4_MODE', False)
STAGE5_mode = BBScorevars.getenv('BBS_STAGE5_MODE', False)

nb_cpu = int(BBScorevars.getenv('BBS_NB_CPU', False, "1"))

