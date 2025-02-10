#!/usr/bin/env python3

import sys
import os
import time
import subprocess

import BBSvars
import BBSbase

def make_meta_dbs():
    ## Following example of BBS-make-OUTGOING.py
    ## Prepare Rexpr (must be a single string with no spaces).
    Rscript_path = os.path.join(BBSvars.BBS_home,
                                'utils',
                                'makeMetaDbs.R')
    Rfun = 'makeMetaDbs'
    OUTGOING_dir = 'OUTGOING'
    db_filepath = 'PROPAGATION_STATUS_DB.txt'
    Rfuncall = f"{Rfun}('{OUTGOING_dir}','{db_filepath}')"
    Rexpr = f"source('{Rscript_path}');{Rfuncall}"

    cmd = BBSbase.Rexpr2syscmd(Rexpr)

    try:
        subprocess.run(cmd, stdout=None, stderr=subprocess.STDOUT, shell=True,
                       check=True)
    except subprocess.CalledProcessError as e:
        print(f'BBS> [generateMetaDbs] Failed at {time.asctime()} . . .')
        print(f'BBS> [generateMetaDbs] Error: {e} . . .')
    return


##############################################################################
### MAIN SECTION
##############################################################################

if __name__ == "__main__":
    if not os.path.isfile('PROPAGATION_STATUS_DB.txt'):
        msg = (
            f'Make sure to be in {BBSvars.Central_rdir.path} and run '
            f'BBS-make-PROPAGATION_STATUS_DB.py before BBS-make-meta.py.'
        )
        sys.exit('=> EXIT.')
    print('BBS> ==============================================================')
    print(f'BBS> [makeMetaDbs] STARTING on {time.asctime()} ...')
    sys.stdout.flush()
    make_meta_dbs()
    print(f'BBS> [makeMetaDbs] DONE on {time.asctime()} ...')

