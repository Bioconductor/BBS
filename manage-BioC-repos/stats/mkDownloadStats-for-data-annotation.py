#! /usr/bin/env python
#

import os

import stats_config
import stats_utils

main_page_file = 'data-annotation.html'
main_page_title = 'Download stats for Bioconductor annotation packages'

def make_DataAnnPkg_page(c):
    pkg_to_Y = stats_utils.make_package_reports(c, 'annotation',
                                                main_page_file,
                                                main_page_title)
    out = open(main_page_file, 'w')
    stats_utils.write_top_asHTML(out, main_page_title, 'main.css')
    out.write('<BODY>\n')

    stats_utils.write_topright_links_asHTML(out,
        'index.html',
        'Download stats for Bioconductor Software packages',
        'data-experiment.html',
        'Download stats for Bioconductor experiment packages')

    out.write('<H1 style="text-align: center;">%s</H1>\n' % main_page_title)
    stats_utils.write_timestamp_asHTML(out)
    out.write('<P><I>')
    out.write('This page monitors Bioconductor annotation package ')
    out.write('downloads from http://bioconductor.org/ over the last ')
    out.write('12 months. ')
    out.write('The number reported next to each package name is the ')
    out.write('<B>number of distinct IPs that &ldquo;hit&rdquo; the ')
    out.write('package over the last 12 months.</B> ')
    #out.write('Core packages (i.e. the BiocInstaller package + ')
    #out.write('packages that get installed the first time ')
    #out.write('<A href="%s">biocLite()</A> is called ' % \
    #          'http://bioconductor.org/docs/install/')
    #out.write('with no arguments) are reported <B>in bold</B>.')
    out.write('</I></P>\n')
    out.write('<HR>\n')

    # Top 30
    out.write('<H2>%s</H2>\n' % 'Top 30')
    stats_utils.write_TotalDownloadsPerPkg_TABLE(out, 'annotation',
                                                 pkg_to_Y.keys(), pkg_to_Y,
                                                 True, 30)
    out.write('<HR>\n')

    # All annotation packages
    out.write('<H2>%s</H2>' % 'All annotation packages')
    stats_utils.write_DownloadsPerMonth_TABLE(c, out,
                                              'All annotation packages',
                                              "biocrepo='annotation'",
                                              'all_annotation_packages.png')
    stats_utils.write_AlphabeticalIndex(out, 'annotation', pkg_to_Y)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

conn = stats_utils.SQL_connectToDB(stats_config.dbfile) 
c = conn.cursor()
os.chdir('/home/biocadmin/public_html/stats')
make_DataAnnPkg_page(c)
c.close()
conn.close()

