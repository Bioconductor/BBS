#!/usr/bin/env python3
##############################################################################
###
### This file is part of the BBS software (Bioconductor Build System).
###
### Author: Hervé Pagès <hpages.on.github@gmail.com>
### Last modification: Sep 13, 2019
###
### manifest module
###

### Trim 'Package:' prefix from every input line so will accept a plain text
### file with 1 package name per line, whether the line is prefixed with
### 'Package:' or not. Raise an exception if the file contains DCF-like lines
### for fields other than 'Package:'.
def read(manifest_path):
    f = open(manifest_path, 'r')
    pkgs = []
    lineno = 0
    for pkg in f:
        lineno += 1
        ## Skip blank and comment lines.
        if pkg.strip() == '' or pkg.startswith('#'):
            continue
        ## Strip the 'Package:' prefix.
        if pkg.startswith('Package:'):
            pkg = pkg[len('Package:'):]
        elif pkg.find(':') >= 0:
            f.close()
            raise Exception('invalid line %d in file \'%s\':\n\n%s' % \
                            (lineno, manifest_path, pkg))
        pkgs.append(pkg.strip())
    f.close()
    return pkgs

