#! /usr/bin/env python

import xml.dom.minidom
import os
import sys

SVN_EXE = "svn"


def getLastChangedRev(wcPath):
    """Return the svn revision number in which the last change
    to working copy wcPath was made.

    We assume that we have read access to the svn repository
    """
    
    #svnCmd = [SVN_EXE, "log", "--xml", wcPath]
    svnCmd = [SVN_EXE, "log", "-rCOMMITTED", "--xml", wcPath]
    
    svnRes = os.popen(' '.join(svnCmd), 'r').read()

    dom = xml.dom.minidom.parseString(svnRes)

    logEntry = dom.getElementsByTagName("logentry")[0]
    revNum = str(logEntry.getAttribute("revision"))
    dateNode = logEntry.getElementsByTagName("date")[0]
    date = dateNode.childNodes[0].data
    return (revNum, date)
    


if __name__ == '__main__':
    """
    Example usage:
    get_SVN_Revision.py some/path/to/a/working/copy
    """
    wcPath = sys.argv[1]
    print getLastChangedRev(wcPath)

