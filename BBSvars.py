##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: May 31, 2023
###

import sys
import os

import bbs.rdir
import bbs.jobs
import BBSutils


hostname0 = bbs.jobs.getHostname().lower()
node_hostname = BBSutils.getenv('BBS_NODE_HOSTNAME', False)
if node_hostname == None:
    node_hostname = hostname0
elif node_hostname.lower() != hostname0:
    print("BBSvars ERROR: Found hostname '%s', '%s' expected!" % \
          (hostname0, node_hostname))
    sys.exit("==> EXIT")

### Just a safety check (global var 'bbs_user' is actually not used
### beyond this check).
bbs_user = BBSutils.getenv('BBS_USER', False)
if bbs_user != None:
    if sys.platform == 'win32':
        user0 = BBSutils.getenv('USERNAME')
    else:
        user0 = BBSutils.getenv('USER')
    if bbs_user != user0:
        print("BBSvars ERROR: BBS running as user '%s', '%s' expected!" % \
              (user0, bbs_user))
        sys.exit("==> EXIT")


##############################################################################
### BBS CORE GLOBAL VARIABLES
##############################################################################

BBS_home = BBSutils.getenv('BBS_HOME')

### All build nodes must define BBS_CURL_CMD.
curl_cmd = BBSutils.getenv('BBS_CURL_CMD')

### BBS_BIOC_VERSION is not necessarily defined (e.g. for the "cran"
### buildtype) in which case 'bioc_version' will be set to None.
bioc_version = BBSutils.getenv('BBS_BIOC_VERSION', False)

buildtype = BBSutils.getenv('BBS_BUILDTYPE', False, default='bioc')

### Timeout limits

default_INSTALL_timeout   =  '2400.0'  # 40 min

if buildtype == 'data-experiment':
    default_BUILD_timeout =  '4800.0'  # 80 min
elif buildtype == 'workflows':
    default_BUILD_timeout = '10800.0'  #  3 h
elif buildtype == 'books':
    default_BUILD_timeout = '18000.0'  #  5 h
elif buildtype == 'bioc-longtests':
    default_BUILD_timeout = '21600.0'  #  6 h
else:
    default_BUILD_timeout =  '2400.0'  # 40 min

if buildtype == 'books':
    default_CHECK_timeout =   '300.0'  #  5 min
else:
    default_CHECK_timeout = default_BUILD_timeout

INSTALL_timeout  = float(BBSutils.getenv('BBS_INSTALL_TIMEOUT',  False,
                                         default_INSTALL_timeout))

BUILD_timeout    = float(BBSutils.getenv('BBS_BUILD_TIMEOUT',    False,
                                         default_BUILD_timeout))

CHECK_timeout    = float(BBSutils.getenv('BBS_CHECK_TIMEOUT',    False,
                                         default_CHECK_timeout))

BUILDBIN_timeout = float(BBSutils.getenv('BBS_BUILDBIN_TIMEOUT', False,
                                         default_INSTALL_timeout))


##############################################################################
### BBS GLOBAL VARIABLES
##############################################################################

work_topdir = BBSutils.getenv('BBS_WORK_TOPDIR')
r_home = BBSutils.getenv('BBS_R_HOME')
r_libs = BBSutils.getenv('R_LIBS', False)

nb_cpu = BBSutils.getenv('BBS_NB_CPU', False, default='1')
install_nb_cpu = BBSutils.getenv('BBS_INSTALL_NB_CPU', False, default=nb_cpu)
buildsrc_nb_cpu = BBSutils.getenv('BBS_BUILD_NB_CPU', False, default=nb_cpu)
checksrc_nb_cpu = BBSutils.getenv('BBS_CHECK_NB_CPU', False, default=nb_cpu)
nb_cpu = int(nb_cpu)
install_nb_cpu = int(install_nb_cpu)
buildsrc_nb_cpu = int(buildsrc_nb_cpu)
checksrc_nb_cpu = int(checksrc_nb_cpu)

extra_check_options = BBSutils.getenv('BBS_EXTRA_CHECK_OPTIONS', False)

transmission_mode = BBSutils.getenv('BBS_PRODUCT_TRANSMISSION_MODE', False,
                                    default='synchronous')
no_transmission = transmission_mode == 'none'
asynchronous_transmission = transmission_mode == 'asynchronous'
synchronous_transmission = transmission_mode == 'synchronous'

dont_push_srcpkgs = BBSutils.getenv('DONT_PUSH_SRCPKGS', False, default='0')
dont_push_srcpkgs = int(dont_push_srcpkgs) != 0

STAGE2_mode = BBSutils.getenv('BBS_STAGE2_MODE', False)
STAGE4_mode = BBSutils.getenv('BBS_STAGE4_MODE', False)
STAGE5_mode = BBSutils.getenv('BBS_STAGE5_MODE', False)

meat_path = BBSutils.getenv('BBS_MEAT_PATH')
r_cmd = BBSutils.getenv('BBS_R_CMD')
rscript_cmd = BBSutils.getenv('BBS_RSCRIPT_CMD', False)
central_base_url = BBSutils.getenv('BBS_CENTRAL_BASEURL')

if not no_transmission:
    ## Define a bunch of RemoteDir objects.
    rsh_cmd = BBSutils.getenv('BBS_RSH_CMD', False)
    rsync_cmd = BBSutils.getenv('BBS_RSYNC_CMD')
    rsync_rsh_cmd = BBSutils.getenv('BBS_RSYNC_RSH_CMD')
    rsync_options = BBSutils.getenv('BBS_RSYNC_OPTIONS')
    MEAT0_rdir = bbs.rdir.RemoteDir('BBS_MEAT0_RDIR',
                     None,
                     BBSutils.getenv('BBS_MEAT0_RDIR'),
                     BBSutils.getenv('BBS_MEAT0_RHOST', False),
                     BBSutils.getenv('BBS_MEAT0_RUSER', False),
                     rsh_cmd, rsync_cmd, rsync_rsh_cmd, rsync_options)
    central_rdir_path = BBSutils.getenv('BBS_CENTRAL_RDIR', False)
    if central_rdir_path == None:
        Central_rdir = bbs.rdir.RemoteDir('BBS_CENTRAL_BASEURL',
                           central_base_url)
    else:
        central_rhost = BBSutils.getenv('BBS_CENTRAL_RHOST', False)
        central_ruser = BBSutils.getenv('BBS_CENTRAL_RUSER', False)
        Central_rdir = bbs.rdir.RemoteDir('BBS_CENTRAL_BASEURL',
                           central_base_url,
                           central_rdir_path, central_rhost, central_ruser,
                           rsh_cmd, rsync_cmd, rsync_rsh_cmd, rsync_options)
    GITLOG_rdir = bbs.rdir.RemoteDir('BBS_GITLOG_RDIR',
                      None,
                      BBSutils.getenv('BBS_GITLOG_RDIR'),
                      BBSutils.getenv('BBS_GITLOG_RHOST', False),
                      BBSutils.getenv('BBS_GITLOG_RUSER', False),
                      rsh_cmd, rsync_cmd, rsync_rsh_cmd, rsync_options)
    products_in_rdir = Central_rdir.subdir('products-in')
    node_id = BBSutils.getenv('BBS_NODE_ID', False, default=node_hostname)
    Node_rdir = products_in_rdir.subdir(node_id)
    install_rdir = Node_rdir.subdir('install')
    buildsrc_rdir = Node_rdir.subdir('buildsrc')
    checksrc_rdir = Node_rdir.subdir('checksrc')
    buildbin_rdir = Node_rdir.subdir('buildbin')

### Used by BBS-prerun.py only

MEAT0_type = int(BBSutils.getenv('BBS_MEAT0_TYPE'))

if MEAT0_type == 1:  # svn-based builds
    manifest_file = BBSutils.getenv('BBS_BIOC_MANIFEST_FILE')
    manifest_path = os.path.join(MEAT0_rdir.path, manifest_file)
    vcsmeta_file = os.path.join('svninfo', 'svn-info.txt')

if MEAT0_type == 3:  # git-based builds
    manifest_git_repo_url = BBSutils.getenv('BBS_BIOC_MANIFEST_GIT_REPO_URL')
    manifest_git_branch = BBSutils.getenv('BBS_BIOC_MANIFEST_GIT_BRANCH')
    manifest_clone_path = BBSutils.getenv('BBS_BIOC_MANIFEST_CLONE_PATH')
    manifest_file = BBSutils.getenv('BBS_BIOC_MANIFEST_FILE')
    manifest_path = os.path.join(manifest_clone_path, manifest_file)
    git_branch = BBSutils.getenv('BBS_BIOC_GIT_BRANCH')
    vcsmeta_file = os.path.join('gitlog', 'git-log.dcf')

update_MEAT0 = BBSutils.getenv('BBS_UPDATE_MEAT0', False, default='0')
update_MEAT0 = int(update_MEAT0) != 0

