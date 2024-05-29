# How to set up a light central node on Jetstream2


## What's a "light" central node?

A light central node (a.k.a. non-building node) only runs `prerun.sh`,
`postrun.sh`, and propagation. It does NOT run the `run.sh` script.

After `prerun.sh` is complete, all the satellite nodes start running `run.sh`
and report their results to the central node.

Once all the satellite nodes are done, the central node generates the
build report and propagates packages. Both the report and packages are
pushed/propagated to master.bioconductor.org.



## Create the VM on Jetstream2

We'll create the VM via the Exosphere interface:
https://jetstream2.exosphere.app/exosphere/

Once connected to Jetstream2 via Exosphere, select allocation BIR190004.

Create a new instance:

- Name: bbscentral1

- Image: Ubuntu 22.04

- Flavor: `m3.medium` (8 CPUs, RAM 30GB, Root Disk 60GB). Note that this is
  probably a little bit oversized for the job (the light central node is not
  actually building or checking packages). Next time maybe try the `m3.quad`
  flavor (4 CPUs, RAM 15GB, Root Disk 20GB).

- Advanced Options:
  - `auto_allocated_network` (default)
  - Public IP Address: Assign a public IP address

Once the VM is created, you should be able to `ssh` to the `exouser` account
on the machine. E.g. to connect to `bbscentral1`:

    exouser@149.165.171.124



## From the exouser account

- Set locale to `en_US.UTF-8`:

    sudo locale-gen en_US.UTF-8
    sudo update-locale LANG=en_US.UTF-8
    sudo reboot

  or, if the above didn't work:

    sudo dpkg-reconfigure locales
    sudo reboot

- Set timezone to NY:

    sudo timedatectl set-timezone America/New_York

  Check the time with `date`. If it gets diplayed in the AM/PM format then
  see `Prepare-Ubuntu-22.04-HOWTO.md` for how to change this to 24-hour
  format.

- Create the `biocbuild` and `biocpush` accounts.

- In Exosphere: Create a volume and attach it to the VM. For `bbscentral1`
  I created an 800GB volume (`bbs1`) but we actually don't need that much
  disk space. 400GB would probably be enough.

- Create the `biocbuild` and `biocpush` folders at the root of the new volume:

    cd /media/volume/bbs1
    mkdir biocbuild
    sudo chown biocbuild:biocbuild biocbuild
    mkdir biocpush
    sudo chown biocpush:biocpush biocpush



## From the biocbuild account

- Install ssh keys (`biocbuild`'s private key + the usual public keys).

- The propagation scripts that we will run from the `biocpush` account will
  need read access to `biocbuild`'s home. Enable this with:

    chmod 755 /home/biocbuild

- Create the following folders in `/media/volume/bbs1/biocbuild/`:
  - `bbs-3.20-bioc`
  - `public_html`
  and the corresponding symlinks in `biocbuild`'s home:
  - from `bbs-3.20-bioc` to `/media/volume/bbs1/biocbuild/bbs-3.20-bioc`
  - from `public_html` to `/media/volume/bbs1/biocbuild/public_html`



## Install and configure Apache2

This requires sudo privileges so needs to be done from the `exouser` account.
See `Prepare-Ubuntu-22.04-HOWTO.md` for the details.



## Back to the biocbuild account

- Clone BBS repo:

    cd
    git clone https://github.com/bioconductor/BBS

- Create `.BBS/` folder with `smtp_config.yaml` in it (copy content from other
  central builder e.g. nebbiolo1 or nebbiolo2).

- Create `bbs-3.20-bioc/log/`.

- Even though this is a non-building node, R is still needed by the `prerun.sh`
  and `postrun.sh` scripts. Download and install it.
  On `bbscentral1`, I downloaded R-4.4.0.tar.gz to `~/rdownloads/` and
  installed it in `~/R/R 4.4/`. Note that this version of R won't need to
  be updated on a regular basis like we do on the satellite nodes.



## Change BBS code

On your local machine, clone the BBS repo and make the following changes:

- Register new `bbscentral1` node in the `nodes/` db.

- To set `bbscentral1` as the central node for the 3.20 software builds,
  add the `BBS/3.20/bioc/bbscentral1/` folder with the following files
  in it: `config.sh`, `prerun.sh`, `postrun.sh`, and `stage7-notify.sh`.
  Then visit all the other `BBS/3.20/bioc` subfolders (one per satellite node)
  and in each of them modify `config.sh` to use `bbscentral1` as central
  node.

- Repeat the above for other builds if necessary (e.g. `workflows`
  and `bioc-longtests`). Note that `stage7-notify.sh` is not needed for
  the `bioc-longtests` builds.

- Commit, push, and deploy on `bbscentral1` and all the satellite nodes.



## Edit the biocbuild crontabs


`bbscentral1` is used as central non-building node for the 3.20 software,
workflows, and long tests builds at the moment (as of May 29, 2024).


### 3.20 software builds

The satellite nodes participating to these builds are:
- `nebbiolo2`: Linux Ubuntu 22.04 machine at DFCI
- `palomino4`: Windows VM on Azure
- `merida1`: Mac x86_64 VM on MacStadium
- `kjohnson1`: Mac arm64 VM (Mac Studio) on MacStadium

Right now, these builds run twice a week only (start on Sunday and
Wednesday mornings, finish on Tuesday and Friday in the afternoon).

See crontabs on `bbscentral1` and all the satellite nodes for the details.


### 3.20 workflows builds

The satellite nodes participating to these builds are: `nebbiolo2` (Linux),
`palomino4` (Windows), `merida1` (Mac x86_64).

These builds run on Tuesdays and Fridays, with report published the same
day (about 4 hrs after the builds started).

See crontabs on `bbscentral1` and all the satellite nodes for the details.


### 3.20 long tests

The satellite nodes participating to these builds are: `nebbiolo2` (Linux),
`palomino4` (Windows), `merida1` (Mac x86_64).

These builds run on Saturdays with report published the same day.

See crontabs on `bbscentral1` and all the satellite nodes for the details.



## Set up staging repos and propagation from the biocpush account

- Install ssh keys (`biocbuild`'s private key + the usual public keys).

- The `postrun.sh` script that we will run from the biocbuild account will
  need read access to `biocpush`'s home. Enable this with:

    chmod 755 /home/biocpush

- Create the `PACKAGES` folder in `/media/volume/bbs1/biocpush` and make
  corresponding symlink in `~biocpush/`.

- Set up propagation (see `Set-up-propagation-HOWTO.md` for the details).
  We only need to do this for the 3.20 software and workflows builds at
  the moment.

- Note that deb package `libxml2-dev` might be needed to install CRAN
  package **XML** required by **biocViews**).

