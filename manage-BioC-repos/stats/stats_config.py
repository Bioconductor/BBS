import os
import datetime

biocrepo2label = { \
    'bioc': "Software", \
    'annotation': "Annotation", \
    'experiment': "Experiment" \
}

biocrepo2subdir = { \
    'bioc': "bioc",
    'annotation': "data-annotation",
    'experiment': "data-experiment"
}

squid_access_logdirs = [os.path.join('bioc-access-logs', 'squid', 'cobra'), os.path.join('bioc-access-logs', 'squid', 'mamba')]

apache2_access_logdirs = [os.path.join('bioc-access-logs', 'apache2', 'krait', 'master')]

s3_access_logdirs = [os.path.join('bioc-access-logs', 's3')]

dbfile = 'pkgdownloads_db.sqlite'

def getLastMonths(n):
    today = datetime.date(2008, 12, 2).today()
    year0 = today.year
    month0 = today.month - n
    if month0 <= 0:
        yeardelta = (-month0) / 12 + 1
        year0 -= yeardelta
        month0 += 12 * yeardelta
    lastmonths = []
    for i in range(n):
        month0 += 1
        if month0 > 12:
            year0 += 1
            month0 -= 12
        yearmonth = datetime.date(year0, month0, 1).strftime('%b/%Y')
        lastmonths.append(yearmonth)
    return lastmonths

lastmonths = getLastMonths(12)

buildnode_ips = [
    '140.107.158.81',  # lamb1
    '140.107.158.83',  # wilson2
    '140.107.158.82',  # wilson1
    '140.107.170.110', # wellington
    '140.107.170.150', # lemming
    '140.107.152.178', # liverpool
    '140.107.170.90',  # gewurz
    '140.107.156.121', # pitt
    '140.107.156.122', # pelham
    '140.107.170.146', # churchill
]

known_fhcrc_machines = {
    '140.107.62.189': 'gopher1',
    '140.107.62.190': 'gopher2',
    '140.107.62.191': 'gopher3',
    '140.107.62.192': 'gopher4',
    '140.107.62.193': 'gopher5',
    '140.107.170.156': 'gopher6',
    '140.107.170.157': 'gopher7',
    '140.107.170.108': 'gladstone',
    '140.107.158.85': 'george1',
    '140.107.158.86': 'george2',
    '140.107.170.103': 'lamprey',
    '140.107.158.64': 'orca1',
    '140.107.158.65': 'orca2',
    '140.107.158.66': 'orca3',
    '140.107.170.112': 'orca4',
    '140.107.170.113': 'orca5',
    '140.107.170.114': 'orca6',
    '140.107.158.121': 'diamondback',
    '140.107.158.78': 'puffadder',
    '140.107.158.120': 'copperhead',
    '140.107.158.84': 'lamb2',
    '140.107.170.116': 'merlot1',
    '140.107.158.54': 'merlot2',
    '140.107.3.11': 'cobra',
    '140.107.3.12': 'mamba',
    '140.107.3.51': 'mamushi',
    '140.107.170.120': 'hedgehog',
    '140.107.156.103': 'derby',
    '140.107.156.104': 'compton',
    '140.107.156.102': 'walpole',
}

# Packages explicitly or implicitly installed by biocLite()
bioclite_pkgs = [
    "BiocInstaller", "BiocGenerics",
    "Biobase", "S4Vectors", "AnnotationDbi", "IRanges"
]

