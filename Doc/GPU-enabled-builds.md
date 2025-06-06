# Running Bioconductor GPU-enabled builds on Jetstream2 (experimental)


Flavor >= g3.medium required for RbowtieCuda (g3.small is not enough)


## 1. From the exouser account

### Check locales

See `BBS/Doc/Prepare-Ubuntu-24.04-HOWTO.md` for the details.

### Install Ubuntu packages

Install all Ubuntu packages listed in `/apt_optional_compile_R.txt`,
`BBS/Ubuntu-files//apt_cran.txt`,  and `BBS/Ubuntu-files/24.04/apt_bioc.txt`:

    BBS_UBUNTU_PATH=
    BBS_PACKAGES_FILE=
    sudo apt install $(cat $BBS_UBUNTU_PATH/$BBS_PACKAGES_FILE | awk '/^[^#]/ {print $1}')

Plus:

    sudo apt install tree  # cause it's nice to have
    sudo apt install pandoc
    sudo apt install texlive-latex-base texlive-fonts-extra

    sudo apt install libthrust-dev libcub-dev  # required by RbowtieCuda

Note: OpenCL (`ocl-icd-opencl-dev`) can break the Nvidia drivers in Jetstream2
that are not available anywhere. If a driver breaks, you will have to submit
a support ticket and ask for the driver to be reinstalled.

#### Holding packages

To prevent accidental removal, the following packages have been held on
`biocgpu`:

    network-manager
    network-manager-config-connectivity-ubuntu
    network-manager-openvpn-gnome
    network-manager-pptp-gnome
    nvidia-linux-grid-535

See `BBS/Doc/Prepare-Ubuntu-24.04-HOWTO.md` for more details on holding.
Removal of Nvidia drivers require you to submit a support ticket
to Jetstream2 for reinstallation.

### Run Xvfb as a service

See `BBS/Doc/Prepare-Ubuntu-24.04-HOWTO.md` for the details.

### Create `biocbuild` account

Create `biocbuild` account.

### Run Apache server as a service

Run Apache server as a service.

Create `/home/biocbuild/public_html/BBS` from the `biocbuild` account.

Set Apache server DocumentRoot.

See `BBS/Doc/Prepare-Ubuntu-24.04-HOWTO.md` for the details.

### Add volume if running release and devel on same machine

Since the default g3.medium has 60GB, it may be necessary to add an extra
volume if running both the release and devel builds. Some of
`/home/biocbuild/bbs-*-bioc-gpu` or `/home/biocpush/PACKAGES` can reside on
the volume.


## 2. From the biocbuild account

- Install the usual stuff in `~/.ssh/`.

- Add the following lines to `~/.profile`:
    ```
    module load nvhpc/24.7/nvhpc
    unset CC CXX F77 F90 FC
    ```
  Logout and login again for the change to take effect.
  Doing `unset CC CXX F77 F90 FC` prevents the NVIDIA compiler from
  becoming the default compiler.
  Note that the NVIDIA compiler is not a substitute for `gcc` in general
  e.g. it cannot be used to compile R or Python or any code that relies
  on compilation flags supported by the latter but not the former.

- Check:
    ```
    nvidia-smi
    nvcc --version
    echo $CC $CXX $F77 $F90 $FC  # should display a blank line
    ```

- Clone BBS:
    ```
    cd
    git clone git@github.com:Bioconductor/BBS
    ```

- Create `bbs-X.Y-bioc-gpu` directory structure e.g.:
    ```
    cd
    mkdir bbs-3.21-bioc-gpu
    cd bbs-3.21-bioc-gpu
    mkdir rdownloads log
    ```

- Install R: See `BBS/Doc/Prepare-Ubuntu-24.04-HOWTO.md` for the details.


## 3. Set up the GPU-enabled builds

For now these builds are running as _standalone_ builds i.e. they run
independently of the daily builds, with their own schedule, and they
produce their own build report. The only thing that they share with
the software daily builds is that they will propagate the package source
tarballs to the software repo.

Only packages with a strong dep on an nvidia GPU (like the **RbowtieCuda**
package) need to be added to these builds. These packages should still
be added to the usual software manifest but they also need to have
a `.BBSoptions` file with the following lines:

    GPU_reliance: required
    UnsupportedPlatforms: win, mac

These package will still show up on the daily software report but they
won't get built/checked on any platform. They will get labelled as
NOT SUPPORTED on Windows and Mac like any other package not supported
on these platforms. On Linux, they won't go thru INSTALL/BUILD/CHECK
either and the report will simply mention that they are being built/checked
somewhere else with a link to the GPU-enabled build report.

Other packages that can take advantage of the presence of a GPU but don't
require it only need to add the following line in their `.BBSoptions` file:

    GPU_reliance: optional


## 4. Set up reviewer account

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

- Add the following lines to `~/.profile`:
    ```
    module load nvhpc/24.7/nvhpc
    unset CC CXX F77 F90 FC
    ```
  Logout and login again for the change to take effect.

- Check:
    ```
    nvidia-smi
    nvcc --version
    echo $CC $CXX $F77 $F90 $FC  # should display a blank line
    ```

- In `~/bin`, create symlinks to the `R` and `Rscript` executables used by
  the GPU-enabled builds. For example:
    ```
    cd ~/bin
    ln -s ~biocbuild/bbs-3.21-bioc-gpu/R/bin/R
    ln -s ~biocbuild/bbs-3.21-bioc-gpu/R/bin/Rscript
    ```

- Start `R` (by just typing `R`) and try to install a Bioconductor package e.g.:
    ```
    library(BiocCheck)
    install("BiocCheck", force=TRUE)
    ```
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


## 5. Alternatively setting up a GPU build using a container

You can run nvidia-based BBS containers at
https://github.com/Bioconductor/bioconductor_salt/pkgs/container/bioconductor_salt.

### 5.1 Prepare the host machine

You must install `nvidia-container-toolkit` to expose the host machine's GPU to
the container. Prior to installing you should have the proper Nvidia drivers
installed and you should be able to use `nvidia-smi` to display the version.

Note: installing the `nvidia-container-toolkit` may alter software on the host
container, so it should be done carefully noting what may be installed or
removed.

    sudo apt install docker nvidia-container-toolkit

After installation, restart the host machine and verify containers are able to
see GPU and do not require sudo:

    docker run --gpus all nvidia/cuda nvidia-smi

You should see output similar to running `nvidia-smi` on the host machine.

Note: You can use `docker ps -a` to show the name of the container and use
`docker rm` to remove it.

### 5.2 Set up biocbuild account

Set up biocbuild account as previously described but set the user id to 1007
as the container assumes this is the user who will run the builds.

    sudo useradd biocbuild -u 1007

Also, set up the `.ssh/config` and add the ssh key.

Note: If 1007 cannot be used as the id, the container should be altered. The
id of the host and container users must be the same.

### 5.3 Initial container run

The container will have volumes mounted to the following locations:

* /home/biocbuild/.ssh
* /home/biocbuild/.cache
* /home/biocbuild/BBS
* /home/biocbuild/bbs-3.22-bioc-gpu

So these locations should exist and the log should be created inside the gpu
build directory.

You can then download the container with

    docker run \
      --name bbscontainer \
      -h amarone \
      --gpus all \
      -v /home/biocbuild/.ssh:/home/biocbuild/.ssh \
      -v /home/biocbuild/.cache:/home/biocbuild/.cache \
      -v /home/biocbuild/bbs-3.22-bioc-gpu:/home/biocbuild/bbs-3.22-bioc-gpu \
      -v /home/biocbuild/BBS:/home/biocbuild/BBS \
      -it ghcr.io/bioconductor/bioconductor_salt:devel-nvidia-noble-24.04-bioc-3.22 bash

You can use this to check if you can create files in the container that will
reside on the host machine as well as use `nvidia-smi` to determine if GPUs are
available to the container.

For example, to check that you can create files in mounted volumes

    docker exec bbscontainer touch /home/biocbuild/bbs-3.22-bioc-gpu/mytmp
    ls /home/biocbuild/bbs-3.22-bioc-gpu/mytmp # on the host machine

Note that because we mount the bioc-gpu directory as a volume, R must be
available in another directory, which is the bioc directory in the container.

The container can be stopped and started with `docker stop bbscontainer` and
`docker start bbscontainer`. You can use `docker exec -it bbscontainer bash` to
start a bash session for troubleshooting.

### 5.4 Run the build for the first time

Run the build with

    docker exec bbscontainer /bin/bash --login -c 'export USER=biocbuild && cd /home/biocbuild/BBS/3.22/bioc-gpu/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.22-bioc-gpu/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'

Note that `USER` is exported. Without it, the build will fail because it expects
to have `USER` available but it does not exist inside the container.

After the initial build, verify all the products are created in the bioc-gpu
directory and that they have been rsynced to the primary builder.

### 5.5 Set up the cronjob

For the cronjob, we same docker command. In the example below, we start and
stop the container; however, it may not be necessary.

    40 03,09,15,21 * * * docker start bbscontainer

    45 03,09,15,21 * * * docker exec bbscontainer /bin/bash --login -c 'export USER=biocbuild && cd /home/biocbuild/BBS/3.22/bioc-gpu/`hostname` && ./run.sh >>/home/biocbuild/bbs-3.22-bioc-gpu/log/`hostname`-`date +\%Y\%m\%d`-run.log 2>&1'

    00 05,11,17,23 * * * docker stop bbscontainer
