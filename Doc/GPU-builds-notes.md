# Running Bioconductor GPU builds on Jetstream2 (experimental)


Flavor >= g3.medium required for RbowtieCuda (g3.small is not enough)


## From the exouser account

### Check locales

See `BBS/Doc/Prepare-Ubuntu-22.04-HOWTO.md` for the details.

### Install Ubuntu packages

Install all Ubuntu packages listed in `BBS/Ubuntu-files/24.04/apt_optional_compile_R.txt`:

    sudo apt install gobjc libpng-dev libjpeg-dev libtiff-dev libcairo2-dev libicu-dev tcl-dev tk-dev default-jdk

Plus:

    sudo apt install tree  # cause it's nice to have
    sudo apt install pandoc
    sudo apt install texlive-latex-base texlive-fonts-extra

    sudo apt install libxml2-dev  # required by CRAN package xml2 and XML
    sudo apt install libthrust-dev libcub-dev  # required by RbowtieCuda

No need to install anything else for now.

### Run Xvfb as a service

See `BBS/Doc/Prepare-Ubuntu-22.04-HOWTO.md` for the details.

### Create `biocbuild` account

Create `biocbuild` account.

### Run Apache server as a service

Run Apache server as a service.

Create `/home/biocbuild/public_html/BBS` from the `biocbuild` account.

Set Apache server DocumentRoot.

See `BBS/Doc/Prepare-Ubuntu-22.04-HOWTO.md` for the details.


## From the biocbuild account

Install the usual stuff in `~/.ssh/`.

Add `module load nvhpc/24.7/nvhpc` to `~/.profile`. Logout and login again
for the change to take effect.

Check:

    nvidia-smi
    nvcc --version

Clone BBS:

    cd
    git clone git@github.com:Bioconductor/BBS

Create `bbs-X.Y-bioc-gpu` directory structure e.g.:

    cd
    mkdir bbs-3.21-bioc-gpu
    cd bbs-3.21-bioc-gpu
    mkdir rdownloads log

Install R:

See `BBS/Doc/Prepare-Ubuntu-22.04-HOWTO.md` for the details.

IMPORTANT: The GPU builds need access to the nvidia compiler (`nvcc` command)
which is provided by the `nvhpc/24.7/nvhpc` module. However, for some reason
the module breaks R configure script so make sure to unload it before
installing R:

    module unload nvhpc/24.7/nvhpc

Once R is compiled/installed, make sure to load the module again:

    module load nvhpc/24.7/nvhpc


## Set up the GPU-enabled builds

WORK-IN-PROGRESS!

Some tweaks to the BBS code will be needed to support the GPU-enabled builds.

In the short term, these builds are going to run as _standalone_ builds i.e.
they will run independently of the daily builds, will have their own schedule,
and will produce their own build report. The only thing that they share with
the software daily builds is that they will propagate the package source
tarballs to the software repo.

Only packages with a strong dep on an nvidia GPU (like the **RbowtieCuda**
package) need to be added to these builds. These packages should still
be added to the usual software manifest but they also need to have
a `.BBSoptions` file with the following lines:

    GPUbuilds: TRUE
    UnsupportedPlatforms: win, mac

These package will still show up on the daily software report but they
won't get built/checked on any platform. They will get labelled as
NOT SUPPORTED on Windows and Mac like any other package not supported
on these platforms. On Linux, they won't go thru INSTALL/BUILD/CHECK
either and the report will simply mention that they are being built/checked
somewhere else with a link to the GPU-enabled build report.


## Set up reviewer account

This is a temporary solution until we come up with something better/safer
that can scale up as more packages with a strong GPU dep get submitted to
Bioconductor.

Create `reviewer` account on the GPU-enabled builder (from the `exouser`
account).

### From the `reviewer` account

- Create `~/.ssh/authorized_keys` and add the usual core team public keys
  to the file (same as on any other build machine). Nothing else goes
  in `~/.ssh/`. In particular NO `id_rsa` or `config` file!

- Create folders `~/bin` and `~/sandbox`.

- Add `module load nvhpc/24.7/nvhpc` to `~/.profile`. Logout and login again
  for the change to take effect.

- Check:
    ```
    nvidia-smi
    nvcc --version
    ```

- In `~/bin`, create symlinks to the `R` and `Rscript` executables used by
  the GPU-enabled builds. For example:

    cd ~/bin
    ln -s ~biocbuild/bbs-3.21-bioc-gpu/R/bin/R
    ln -s ~biocbuild/bbs-3.21-bioc-gpu/R/bin/Rscript

- Start `R` (by just typing `R`) and try to install a Bioconductor package e.g.:

    library(BiocCheck)
    install("BiocCheck", force=TRUE)

  This will ask you if you'd like to create a personal library. Answer yes.

### For each review

- Add the reviewer's public key to `~/.ssh/authorized_keys`.

- Give them the ssh command to connect to the machine e.g.
    ```
    ssh -A reviewer@149.165.152.218
    ```
  for access to biocgpu.

- Delete their public key from `~/.ssh/authorized_keys` when they're done.

Preferrably only one reviewer at a time should work on the machine so they
don't step on each other toes.

