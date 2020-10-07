##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Oct 6, 2020
###

import sys
import os

import bbs.rdir
import bbs.jobs
import BBSutils


### Just a safety check. Global var 'user' is actually not used.
if sys.platform == "win32":
    running_user = BBSutils.getenv('USERNAME')
else:
    running_user = BBSutils.getenv('USER')
user = BBSutils.getenv('BBS_USER', False, running_user)
if user != running_user:
    print("BBSvars ERROR: BBS running as user '%s', '%s' expected!" % \
          (running_user, user))
    sys.exit("==> EXIT")


##############################################################################
### BBS CORE GLOBAL VARIABLES
##############################################################################


BBS_home = BBSutils.getenv('BBS_HOME')
### BBS_BIOC_VERSION is not necessarily defined (e.g. for the "cran"
### subbuilds) in which case 'bioc_version' will be set to None.
bioc_version = BBSutils.getenv('BBS_BIOC_VERSION', False)

subbuilds = BBSutils.getenv('BBS_SUBBUILDS', False, "bioc")

### Timeout limits

default_INSTALL_timeout   =  "2400.0"  # 40 min

if subbuilds == "data-experiment":
    default_BUILD_timeout =  "4800.0"  # 80 min
elif subbuilds == "workflows":
    default_BUILD_timeout =  "7200.0"  #  2 h
elif subbuilds == "books":
    default_BUILD_timeout = "18000.0"  #  5 h
elif subbuilds == "bioc-longtests":
    default_BUILD_timeout = "21600.0"  #  6 h
else:
    default_BUILD_timeout =  "2400.0"  # 40 min

INSTALL_timeout  = float(BBSutils.getenv('BBS_INSTALL_TIMEOUT',  False,
                                         default_INSTALL_timeout))

BUILD_timeout    = float(BBSutils.getenv('BBS_BUILD_TIMEOUT',    False,
                                         default_BUILD_timeout))

CHECK_timeout    = float(BBSutils.getenv('BBS_CHECK_TIMEOUT',    False,
                                         default_BUILD_timeout))

BUILDBIN_timeout = float(BBSutils.getenv('BBS_BUILDBIN_TIMEOUT', False,
                                         default_INSTALL_timeout))


##############################################################################
### BBS GLOBAL VARIABLES
##############################################################################

ssh_cmd = BBSutils.getenv('BBS_SSH_CMD', False)
rsync_cmd = BBSutils.getenv('BBS_RSYNC_CMD')
rsync_rsh_cmd = BBSutils.getenv('BBS_RSYNC_RSH_CMD')

central_rdir_path = BBSutils.getenv('BBS_CENTRAL_RDIR', False)
if central_rdir_path == None:
    Central_rdir = bbs.rdir.RemoteDir('BBS_CENTRAL_BASEURL',
                    BBSutils.getenv('BBS_CENTRAL_BASEURL'),
                    None,
                    None,
                    None,
                    None, None, None)
else:
    central_rhost = BBSutils.getenv('BBS_CENTRAL_RHOST', False)
    central_ruser = BBSutils.getenv('BBS_CENTRAL_RUSER', False)
    Central_rdir = bbs.rdir.RemoteDir('BBS_CENTRAL_BASEURL',
                    BBSutils.getenv('BBS_CENTRAL_BASEURL'),
                    central_rdir_path,
                    central_rhost,
                    central_ruser,
                    ssh_cmd, rsync_cmd, rsync_rsh_cmd)

nodes_rdir = Central_rdir.subdir('nodes')

### Only needed by BBS-prerun.py and BBS-run.py

MEAT0_rdir = bbs.rdir.RemoteDir('BBS_MEAT0_RDIR',
                None,
                BBSutils.getenv('BBS_MEAT0_RDIR'),
                BBSutils.getenv('BBS_MEAT0_RHOST', False),
                BBSutils.getenv('BBS_MEAT0_RUSER', False),
                ssh_cmd,
                rsync_cmd,
                rsync_rsh_cmd)

meat_path = BBSutils.getenv('BBS_MEAT_PATH')

work_topdir = BBSutils.getenv('BBS_WORK_TOPDIR')

r_cmd = BBSutils.getenv('BBS_R_CMD')

r_home = BBSutils.getenv('BBS_R_HOME')

### Only needed by BBS-prerun.py

MEAT0_type = int(BBSutils.getenv('BBS_MEAT0_TYPE'))

if MEAT0_type == 1:  # svn-based builds
    manifest_file = BBSutils.getenv('BBS_BIOC_MANIFEST_FILE')
    manifest_path = os.path.join(MEAT0_rdir.path, manifest_file)
    vcsmeta_file = 'svninfo/svn-info.txt'

if MEAT0_type == 3:  # git-based builds
    manifest_git_repo_url = BBSutils.getenv('BBS_BIOC_MANIFEST_GIT_REPO_URL')
    manifest_git_branch = BBSutils.getenv('BBS_BIOC_MANIFEST_GIT_BRANCH')
    manifest_clone_path = BBSutils.getenv('BBS_BIOC_MANIFEST_CLONE_PATH')
    manifest_file = BBSutils.getenv('BBS_BIOC_MANIFEST_FILE')
    manifest_path = os.path.join(manifest_clone_path, manifest_file)
    git_branch = BBSutils.getenv('BBS_BIOC_GIT_BRANCH')
    vcsmeta_file = 'gitlog/git-log.dcf'

update_MEAT0 = int(BBSutils.getenv('BBS_UPDATE_MEAT0', False, "0")) != 0

### Only needed by BBS-run.py

STAGE2_r_script = BBSutils.getenv('BBS_STAGE2_R_SCRIPT')

hostname0 = bbs.jobs.getHostname()
node_hostname = BBSutils.getenv('BBS_NODE_HOSTNAME', False, hostname0)
### Check that 'node_hostname' matches the effective hostname:
if node_hostname.lower() != hostname0.lower():
    print("BBSvars ERROR: Found hostname '%s', '%s' expected!" % (hostname0, node_hostname))
    sys.exit("==> EXIT")

node_id = BBSutils.getenv('BBS_NODE_ID', False, node_hostname)
Node_rdir = nodes_rdir.subdir(node_id)
install_rdir = Node_rdir.subdir('install')
buildsrc_rdir = Node_rdir.subdir('buildsrc')
checksrc_rdir = Node_rdir.subdir('checksrc')
buildbin_rdir = Node_rdir.subdir('buildbin')

STAGE2_mode = BBSutils.getenv('BBS_STAGE2_MODE', False)
STAGE4_mode = BBSutils.getenv('BBS_STAGE4_MODE', False)
STAGE5_mode = BBSutils.getenv('BBS_STAGE5_MODE', False)

nb_cpu = BBSutils.getenv('BBS_NB_CPU', False, "1")
check_nb_cpu = BBSutils.getenv('BBS_CHECK_NB_CPU', False, nb_cpu)
nb_cpu = int(nb_cpu)
check_nb_cpu = int(check_nb_cpu)

GITLOG_rdir = bbs.rdir.RemoteDir('BBS_GITLOG_RDIR',
                None,
                BBSutils.getenv('BBS_GITLOG_RDIR'),
                BBSutils.getenv('BBS_GITLOG_RHOST', False),
                BBSutils.getenv('BBS_GITLOG_RUSER', False),
                ssh_cmd,
                rsync_cmd,
                rsync_rsh_cmd)

