#! /usr/bin/env python
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Jan 17, 2008
###

import sys
import time

import bbs.email

import BBScorevars
import BBSreportutils

from_addr = "BBS-noreply@bioconductor.org"

msg_head = "[This is an automatically generated email. Please don't reply.]\n"

msg_tail = "Please take the time to address this then use your Subversion account\n" \
         + "when you are ready to commit a fix to your package.\n"

msg_footnote = "Notes:\n\n" \
             + "  * This was the status of your package at the time this email was sent to you.\n" \
             + "    Given that the online report is updated daily (in normal conditions) you\n" \
             + "    could see something different when you visit the URL(s) above, especially if\n" \
             + "    you do so several days after you received this email.\n\n" \
             + "  * It is possible that the problems reported in this report are false positives,\n" \
             + "    either because another package (from CRAN or Bioconductor) breaks your\n" \
             + "    package (if yours depends on it) or because of a Build System problem.\n" \
             + "    If this is the case, then you can ignore this email.\n\n" \
             + "  * Please check the report again 24h after you've committed your changes to the\n" \
             + "    package and make sure that all the problems have gone.\n\n" \
             + "  * If you have questions about this report or need help with the\n" \
             + "    maintenance of your package, please use the Bioc-devel mailing list:\n\n" \
             + "      https://bioconductor.org/help/mailing-list/\n\n" \
             + "    (all package maintainers are requested to subscribe to this list)\n\n" \
             + "For immediate notification of package build status, please\n" \
             + "subscribe to your package's RSS feed. Information is at:\n\n" \
             + "https://bioconductor.org/developers/rss-feeds/\n\n" \
             + "Thanks for contributing to the Bioconductor project!\n\n" 

def send_notification(pkg):
    package_status = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'PackageStatus')
    if package_status == 'Deprecated':
        return
    maintainer_email = BBSreportutils.get_pkg_field_from_meat_index(pkg, 'MaintainerEmail')
    #print "%s %s %s %s" % (pkg, version, maintainer, maintainer_email)
    #key = 'Last Changed Date'
    #last_changed_date = BBSreportutils.get_vcs_meta(pkg, key)
    #key = 'Last Changed Rev'
    #last_changed_rev = BBSreportutils.get_vcs_meta(pkg, key)
    problem_descs = []
    for node in BBSreportutils.supported_nodes(pkg):
        stagecmd = 'install'
        status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
        if status in ["TIMEOUT", "ERROR"]:
            leafreport_rURL = BBSreportutils.get_leafreport_rURL(pkg, node.id, stagecmd)
            problem_desc = "  o %s for 'R CMD INSTALL' on %s. See the details here:\n" % (status, node.id) \
                         + "      %s%s\n" % (BBSreportutils.data_source, leafreport_rURL)
            problem_descs.append(problem_desc)
        stagecmd = 'buildsrc'
        status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
        if status in ["TIMEOUT", "ERROR"]:
            leafreport_rURL = BBSreportutils.get_leafreport_rURL(pkg, node.id, stagecmd)
            problem_desc = "  o %s for 'R CMD build' on %s. See the details here:\n" % (status, node.id) \
                         + "      %s%s\n" % (BBSreportutils.data_source, leafreport_rURL)
            problem_descs.append(problem_desc)
        stagecmd = 'checksrc'
        status = BBSreportutils.get_status_from_db(pkg, node.id, stagecmd)
        if status in ["TIMEOUT", "ERROR"]:
            leafreport_rURL = BBSreportutils.get_leafreport_rURL(pkg, node.id, stagecmd)
            problem_desc = "  o %s for 'R CMD check' on %s. See the details here:\n" % (status, node.id) \
                         + "      %s%s\n" % (BBSreportutils.data_source, leafreport_rURL)
            problem_descs.append(problem_desc)
    if len(problem_descs) == 0:
        return
    if maintainer_email == "bioconductor@stat.math.ethz.ch":
        to_addrs = ["devteam-bioc@lists.fhcrc.org"]
    else:
        to_addrs = [maintainer_email]
    subject = "%s problems reported by the \"%s\" for %s" \
              % (pkg, main_page_title, BBSreportutils.get_build_label())
    msg = "%s\nHi %s maintainer,\n\n" % (msg_head, pkg) \
        + "According to the \"%s\" for %s,\n" % (main_page_title, BBSreportutils.get_build_label()) \
        + "the %s package has the following problem(s):\n\n" % pkg \
        + "%s\n%s\n%s" % ('\n'.join(problem_descs), msg_tail, msg_footnote)
    if arg1 == "":
        print "###########################################################"
        print "maintainer_email: %s\n" % maintainer_email
        print "subject: %s\n" % subject
        print msg
        print ""
    bbs.email.sendtextmail(from_addr, to_addrs, subject, msg)
    return

def send_notifications(allpkgs):
    for pkg in allpkgs:
        send_notification(pkg)
    return

def send_BioC_notifications(allpkgs):
    print "BBS> [send_BioC_notifications] BEGIN..."
    send_notifications(allpkgs)
    print "BBS> [send_BioC_notifications] END."
    return

def send_CRAN_notifications(allpkgs):
    print "BBS> [send_CRAN_notifications] BEGIN..."
    send_notifications(allpkgs)
    print "BBS> [send_CRAN_notifications] END."
    return


##############################################################################
### MAIN SECTION
##############################################################################

print "BBS> [stage9] STARTING stage9 at %s..." % time.asctime()

BBSreportutils.data_source = BBScorevars.getenv('BBS_PUBLISHED_REPORT_URL')
notify_nodes = BBScorevars.getenv('BBS_NOTIFY_NODES')

argc = len(sys.argv)
if argc > 1:
    arg1 = sys.argv[1]
else:
    arg1 = ""

if arg1 != "":
    bbs.email.mode = "do-it"
    if arg1 != "do-it":
        bbs.email.redirect_to_addr = arg1

BBSreportutils.set_NODES(notify_nodes)
if len(BBSreportutils.NODES) != 1:
    main_page_title = 'Multiple platform build/check report'
else:
    main_page_title = 'Build/check report'
allpkgs = BBSreportutils.get_pkgs_from_meat_index()
print "BBS> [stage9] Notifying package maintainers for nodes: %s" % notify_nodes
if BBScorevars.mode in ["bioc", "biocLite", "data-experiment"]:
    send_BioC_notifications(allpkgs)
else: # "cran" mode
    send_CRAN_notifications(allpkgs)

print "BBS> [stage9] DONE at %s." % time.asctime()

