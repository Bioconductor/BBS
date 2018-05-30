##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: May 17, 2018
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

r_home = BBScorevars.getenv('BBS_R_HOME')

### Only needed by BBS-prerun.py

MEAT0_type = int(BBScorevars.getenv('BBS_MEAT0_TYPE'))

if MEAT0_type == 1:  # svn-based builds
    manifest_file = BBScorevars.getenv('BBS_BIOC_MANIFEST_FILE')
    manifest_path = os.path.join(MEAT0_rdir.path, manifest_file)
    vcsmeta_file = 'svninfo/svn-info.txt'

if MEAT0_type == 3:  # git-based builds
    manifest_git_repo_url = BBScorevars.getenv('BBS_BIOC_MANIFEST_GIT_REPO_URL')
    manifest_git_branch = BBScorevars.getenv('BBS_BIOC_MANIFEST_GIT_BRANCH')
    manifest_clone_path = BBScorevars.getenv('BBS_BIOC_MANIFEST_CLONE_PATH')
    manifest_file = BBScorevars.getenv('BBS_BIOC_MANIFEST_FILE')
    manifest_path = os.path.join(manifest_clone_path, manifest_file)
    git_branch = BBScorevars.getenv('BBS_BIOC_GIT_BRANCH')
    vcsmeta_file = 'GITLOG0/git-log.txt'

update_MEAT0 = int(BBScorevars.getenv('BBS_UPDATE_MEAT0', False, "0")) != 0

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

nb_cpu = BBScorevars.getenv('BBS_NB_CPU', False, "1")
check_nb_cpu = BBScorevars.getenv('BBS_CHECK_NB_CPU', False, nb_cpu)
nb_cpu = int(nb_cpu)
check_nb_cpu = int(check_nb_cpu)

GITLOG0_rdir = bbs.rdir.RemoteDir('BBS_GITLOG0_RDIR',
                None,
                BBScorevars.getenv('BBS_GITLOG0_RDIR'),
                BBScorevars.getenv('BBS_GITLOG0_RHOST', False),
                BBScorevars.getenv('BBS_GITLOG0_RUSER', False),
                BBScorevars.ssh_cmd,
                BBScorevars.rsync_cmd,
                BBScorevars.rsync_rsh_cmd)

gitlog_path = BBScorevars.getenv('BBS_GITLOG_PATH')
