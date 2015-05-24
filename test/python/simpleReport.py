#!/usr/bin/env python

import os.path
import sys
import HyperText.HTML as ht
import dcf
import urllib

class PackageReport(object):
    def __init__(self, reportUrl):
        reportFile = urllib.urlopen(reportUrl)
        data = dcf.DcfRecordParser(reportFile)
        self.name = data.getValue("Package")
        self.version = data.getValue("Version")

        self.status = data.getValue("Status")
        ## FIXME: we should really define CSS classes for 
        ##        these elements and then let the color be defined in 
        ##        a CSS style file.
        if self.status == "OK":
            self.statusColor = "green"
        else:
            self.statusColor = "red"

        self.time = data.getValue("Time")
        urlBase = os.path.dirname(reportUrl)
        self.outputUrl = urlBase + '/' + self.name + '-out.txt'
        
    def __str__(self):
        """an example str method"""
        return self.name + ' ' + self.version + ' ' + self.outputUrl

    def toHtml(self):
        """Eventually, this method will return the HTML text for
        representing this report as an HTML table row
        """
        tableRow = ht.TR()
        tableRow.append(ht.TD(self.name))
        tableRow.append(ht.TD(self.version))
        ## FIXME: want to use CSS classes and not define color explicitly
        status = ht.FONT(self.status, color=self.statusColor)
        tableRow.append(ht.TD(ht.A(status, href=self.outputUrl)))
        return tableRow


def main(args):
    root_url = args[0]
    report_list_file = urllib.urlopen(root_url + '/' + args[1])
    report_list = []
    for line in report_list_file:
        line = line.strip()
        report_list.append(root_url + '/' + line)

    htTable = ht.TABLE()
    for i in range(5):
        report = PackageReport(report_list[i])
        ##print report
        htTable.append(report.toHtml())
    print ht.HTML(ht.BODY(htTable))


if __name__ == '__main__':
    main(sys.argv[1:])
