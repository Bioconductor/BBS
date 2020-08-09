#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Herve Pages (hpages@fhcrc.org)
### Last modification: Jan 17, 2008
###

import sys
import time

import bbs.notify

import BBScorevars
import BBSreportutils

from_addr = "BBS-noreply@bioconductor.org"

msg_head = "[This is an automatically generated email. Please don't reply.]\n"

msg_tail = "Please take the time to address this by committing and pushing\n" \
         + "changes to your package at git.bioconductor.org\n"

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
    #print("%s %s %s %s" % (pkg, version, maintainer, maintainer_email))
    #key = 'Last Changed Date'
    #last_changed_date = BBSreportutils.get_vcs_meta(pkg, key)
    #key = 'Last Changed Rev'
    #last_changed_rev = BBSreportutils.get_vcs_meta(pkg, key)
    problem_descs = []
    for node in BBSreportutils.supported_nodes(pkg):
        stage = 'install'
        status = BBSreportutils.get_pkg_status(pkg, node.id, stage)
        if status in ["TIMEOUT", "ERROR"]:
            leafreport_rURL = BBSreportutils.get_leafreport_rel_url(pkg, node.id, stage)
            problem_desc = "  o %s for 'R CMD INSTALL' on %s. See the details here:\n" % (status, node.id) \
                         + "      %s%s\n" % (BBSreportutils.data_source, leafreport_rURL)
            problem_descs.append(problem_desc)
        stage = 'buildsrc'
        status = BBSreportutils.get_pkg_status(pkg, node.id, stage)
        if status in ["TIMEOUT", "ERROR"]:
            leafreport_rURL = BBSreportutils.get_leafreport_rel_url(pkg, node.id, stage)
            problem_desc = "  o %s for 'R CMD build' on %s. See the details here:\n" % (status, node.id) \
                         + "      %s%s\n" % (BBSreportutils.data_source, leafreport_rURL)
            problem_descs.append(problem_desc)
        stage = 'checksrc'
        status = BBSreportutils.get_pkg_status(pkg, node.id, stage)
        if status in ["TIMEOUT", "ERROR"]:
            leafreport_rURL = BBSreportutils.get_leafreport_rel_url(pkg, node.id, stage)
            problem_desc = "  o %s for 'R CMD check' on %s. See the details here:\n" % (status, node.id) \
                         + "      %s%s\n" % (BBSreportutils.data_source, leafreport_rURL)
            problem_descs.append(problem_desc)
    if len(problem_descs) == 0:
        return

    report_nodes = BBScorevars.getenv('BBS_REPORT_NODES')
    report_title = BBSreportutils.make_report_title(BBScorevars.subbuilds,
                                                    report_nodes)
    if maintainer_email == "bioconductor@stat.math.ethz.ch":
        to_addrs = ["devteam-bioc@lists.fhcrc.org"]
    else:
        to_addrs = [maintainer_email]
    subject = "%s problems reported in the %s" % (pkg, report_title)
    msg = "%s\nHi %s maintainer,\n\n" % (msg_head, pkg) \
        + "According to the %s,\n" % report_title \
        + "the %s package has the following problem(s):\n\n" % pkg \
        + "%s\n%s\n%s" % ('\n'.join(problem_descs), msg_tail, msg_footnote)
    if arg1 == "":
        print("###########################################################")
        print("maintainer_email: %s\n" % maintainer_email)
        print("subject: %s\n" % subject)
        print(msg)
        print()
    print("BBS> Notifying maintainer(s) of %s:" % pkg)
    sys.stdout.flush()
    bbs.notify.sendtextmail(from_addr, to_addrs, subject, msg)
    return

def send_notifications(allpkgs):
    for pkg in allpkgs:
        send_notification(pkg)
    return

def send_BioC_notifications(allpkgs):
    print("BBS> [send_BioC_notifications] BEGIN...")
    send_notifications(allpkgs)
    print("BBS> [send_BioC_notifications] END.")
    return

def send_CRAN_notifications(allpkgs):
    print("BBS> [send_CRAN_notifications] BEGIN...")
    send_notifications(allpkgs)
    print("BBS> [send_CRAN_notifications] END.")
    return


##############################################################################
### MAIN SECTION
##############################################################################

print("BBS> [stage9] STARTING stage9 at %s..." % time.asctime())

BBSreportutils.data_source = BBScorevars.getenv('BBS_PUBLISHED_REPORT_URL')
notify_nodes = BBScorevars.getenv('BBS_NOTIFY_NODES')

argc = len(sys.argv)
if argc > 1:
    arg1 = sys.argv[1]
else:
    arg1 = ""

if arg1 != "":
    bbs.notify.mode = "do-it"
    if arg1 != "do-it":
        bbs.notify.redirect_to_addr = arg1

BBSreportutils.set_NODES(notify_nodes)
allpkgs = BBSreportutils.get_pkgs_from_meat_index()

print("BBS> [stage9] Import package statuses from %s ..." % \
      BBSreportutils.STATUS_DB_file, end=" ")
sys.stdout.flush()
BBSreportutils.import_STATUS_DB(allpkgs)
print("OK")
sys.stdout.flush()

print("BBS> [stage9] Notifying package maintainers for nodes: %s" % notify_nodes)
if BBScorevars.subbuilds in ["bioc", "data-experiment"]:
    send_BioC_notifications(allpkgs)
else: # "cran" subbuilds
    send_CRAN_notifications(allpkgs)

print("BBS> [stage9] DONE at %s." % time.asctime())

