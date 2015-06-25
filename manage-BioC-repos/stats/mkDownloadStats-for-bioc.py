#! /usr/bin/env python
#

import os

import stats_config
import stats_utils

main_page_file = 'index.html'
main_page_title = 'Download stats for Bioconductor Software packages'

def make_SoftwarePkg_page(c):
    pkg_to_Y = stats_utils.make_package_reports(c, 'bioc',
                                                main_page_file,
                                                main_page_title)
    out = open(main_page_file, 'w')
    stats_utils.write_top_asHTML(out, main_page_title, 'main.css')
    out.write('<BODY>\n')

    stats_utils.write_topright_links_asHTML(out,
        'data-annotation.html',
        'Download stats for Bioconductor annotation packages',
        'data-experiment.html',
        'Download stats for Bioconductor experiment packages')

    out.write('<H1 style="text-align: center;">%s</H1>\n' % main_page_title)
    stats_utils.write_timestamp_asHTML(out)
    out.write('<P><I>')
    out.write('This page monitors Bioconductor Software package ')
    out.write('downloads from http://bioconductor.org/ over the last ')
    out.write('12 months. ')
    out.write('The number reported next to each package name is the ')
    out.write('<B>number of distinct IPs that &ldquo;hit&rdquo; the ')
    out.write('package over the last 12 months.</B> ')
    out.write('Core packages (i.e. the BiocInstaller package + ')
    out.write('packages that get installed the first time ')
    out.write('<A href="%s">biocLite()</A> is called ' % \
              'http://bioconductor.org/docs/install/')
    out.write('with no arguments) are reported <B>in bold</B>.')
    out.write('</I></P>\n')
    out.write('<HR>\n')

    # Top 75
    out.write('<H2>%s</H2>\n' % 'Top 75')
    stats_utils.write_TotalDownloadsPerPkg_TABLE(out, 'bioc',
                                                 pkg_to_Y.keys(), pkg_to_Y,
                                                 True, 75)
    out.write('<HR>\n')

    # All Software packages
    out.write('<H2>%s</H2>' % 'All Software packages')
    stats_utils.write_DownloadsPerMonth_TABLE(c, out,
                                              'All Software packages',
                                              "biocrepo='bioc'",
                                              'all_bioc_packages.png')
    stats_utils.write_AlphabeticalIndex(out, 'bioc', pkg_to_Y)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

def make_main_page():
    out = open(main_page_file, 'w')
    stats_utils.write_top_asHTML(out, main_page_title, 'main.css')
    out.write('<BODY>\n')
    out.write('<H1 style="text-align: center;">%s</H1>\n' % main_page_title)
    out.write('<H2>Global stats</H2>')
    title = 'All packages'
    barplot_file = 'all_packages.png'
    stats_utils.write_DownloadsPerMonth_TABLE(c, out, title,
                                              "package IS NOT NULL",
                                              barplot_file, 700000)
    title = 'All Software packages'
    barplot_file = 'all_bioc_packages.png'
    stats_utils.write_DownloadsPerMonth_TABLE(c, out, title,
                                              "biocrepo='bioc'",
                                              barplot_file, 700000)
    title = 'All Annotation, CDF and Probe packages'
    barplot_file = 'all_data_annotation_packages.png'
    stats_utils.write_DownloadsPerMonth_TABLE(c, out, title,
                                              "biocrepo='annotation'",
                                              barplot_file, 700000)
    title = 'All Experiment Packages'
    barplot_file = 'all_data_experiment_packages.png'
    stats_utils.write_DownloadsPerMonth_TABLE(c, out, title,
                                              "biocrepo='experiment'",
                                              barplot_file, 700000)
    out.write('<H2>%s</H2>' % 'Software packages')
    pkg_to_Y = stats_utils.make_package_reports(c, 'bioc',
                                                main_page_file,
                                                main_page_title)
    stats_utils.write_TotalDownloadsPerPkg_TABLE(out, 'bioc',
                                                 pkg_to_Y.keys(), pkg_to_Y)
    out.write('<H2>%s</H2>' % 'Annotation, CDF and Probe packages')
    pkg_to_Y = stats_utils.make_package_reports(c, 'annotation',
                                                main_page_file,
                                                main_page_title)
    stats_utils.write_TotalDownloadsPerPkg_TABLE(out, 'annotation',
                                                 pkg_to_Y.keys(), pkg_to_Y)
    out.write('<H2>%s</H2>' % 'Experiment packages')
    pkg_to_Y = stats_utils.make_package_reports(c, 'experiment',
                                                main_page_file,
                                                main_page_title)
    stats_utils.write_TotalDownloadsPerPkg_TABLE(out, 'experiment',
                                                 pkg_to_Y.keys(), pkg_to_Y)
    out.write('</BODY>\n')
    out.write('</HTML>\n')
    out.close()
    return

conn = stats_utils.SQL_connectToDB(stats_config.dbfile) 
c = conn.cursor()
os.chdir('/home/biocadmin/public_html/stats')
make_SoftwarePkg_page(c)
#make_main_page()
c.close()
conn.close()

