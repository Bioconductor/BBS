<#
prerequisites:
a windows server 2012 r2 machine with
cygwin installed, specifically rsync, curl, and ssh
(and optionally vim) and in the path
We have an AMI like this (ami-59bf1f32)


COMPUTER_NAME should be set 
to the name this machine should have
(without the domain name)

if you are going to run this as a script, you need
to run this line in a powershell window first:
Set-ExecutionPolicy RemoteSigned

Before running this, you should make another
script based on config-example.ps1 (in this 
directory) called config.ps1, edit the values
to match your system, then source it like this:

. .\config.ps1

Then run this script.

#>

# rename computer; this requires a reboot to take effect ;-(
Rename-Computer -NewName $Env:COMPUTER_NAME

# set domain name (hopefully the hardcoded value is ok)
[Environment]::SetEnvironmentVariable("userdnsdomain", "bioconductor.org", "Machine")

# put it into the environment right away:
$env:userdnsdomain = "bioconductor.org"

# set time zone, may want to customize this
tzutil.exe /s "US Eastern Standard Time"

$download_dir = "c:\Users\Administrator\Downloads"
cd $download_dir

$curl = "c:\cygwin64\bin\curl"

# perl

iex "$curl -LO http://downloads.activestate.com/ActivePerl/releases/5.20.2.2002/ActivePerl-5.20.2.2002-MSWin32-x86-64int-299195.msi"

.\ActivePerl-5.20.2.2002-MSWin32-x86-64int-299195.msi INSTALLDIR=c:\Perl /qb

# add to path AT THE BEGINNING so other perls are not found
$path = ";c:\Perl\bin;" +  $path

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# associate .pl extension with perl scripts:
# does this have to be done as biocbuild as well?

cmd /c "assoc .pl=PerlScript"
cmd /c 'ftype PerlScript=C:\perl\bin\perl.exe "%1" %*'



iex "$curl -LO https://github.com/msysgit/msysgit/releases/download/Git-1.9.5-preview20150319/Git-1.9.5-preview20150319.exe"

.\Git-1.9.5-preview20150319.exe /verysilent

# add git to path
$path = $Env:Path

$path += ";C:\Program Files (x86)\Git\bin"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

iex "$curl -LO https://s3.amazonaws.com/bioc-windows-setup/SlikSvn.zip"

unzip .\SlikSvn.zip -d "C:\Program Files (x86)"

$path += ";C:\Program Files (x86)\SlikSvn\bin"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

mkdir \biocbld

# FIXME - in future we probably want to check this out
# from svn, not git
git clone https://github.com/Bioconductor/BBS.git c:\biocbld\BBS

cd \biocbld\BBS
# this should be temporary:
git checkout start-linux1

cd $download_dir

mkdir \biocbld\.BBS

echo "You have to manually add c:\.BBS\id_rsa!!!!"

net user biocbuild "$Env:BIOCBUILD_PASSWORD" /ADD

# give biocbuild the right to log on 
net localgroup "Remote Desktop Users" biocbuild /add

# install python
iex "$curl -LO http://downloads.activestate.com/ActivePython/releases/2.7.8.10/Acti
vePython-2.7.8.10-win32-x86.msi"

 .\ActivePython-2.7.8.10-win32-x86.msi INSTALLDIR=c:\Python27 /qb

# add to path
$path += ";c:\Python27"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path


#cd "c:\biocbld\BBS\$Env:BIOC_VERSION"

# no point, SET statements in bat file are ignored....


iex "$curl -LO https://cran.rstudio.com/bin/windows/Rtools/Rtools$env:RTOOLS_VERSION.exe"

iex " .\Rtools$env:RTOOLS_VERSION.exe /verysilent"

$path = "C:\Rtools\bin;C:\Rtools\gcc-4.6.3\bin;" + $path

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

$bioc_basedir = "c:\biocbld\bbs-$env:BIOC_VERSION-bioc"
$exp_basedir = "c:\biocbld\bbs-$env:BIOC_VERSION-data-experiment"


mkdir $bioc_basedir
mkdir $exp_basedir

cd $bioc_basedir

mkdir log
# need to create NodeInfo dir as biocbuild:
Start-Process mkdir -Credential biocbuild -ArgumentList "$bioc_basedir\NodeInfo"

# BTW, sometimes the Start-Process line fails with 
# an error about an invalid directory. The solution
# is to close the powershell window and open a new one.

cd $exp_basedir
mkdir log
Start-Process mkdir -Credential biocbuild -ArgumentList "$exp_basedir\NodeInfo"




# mkdir tmp 
# mkdir tmpdir
# mkdir meat

cd $download_dir

$r_basedir = "$bioc_basedir\R"
$r = "$r_basedir\bin\R"

iex "$curl -LO $env:R_URL"

iex ".\$env:R_INSTALLER /DIR=$r_basedir /noicons /verysilent"

# biocbuild user should MANUALLY add R to their user path
# or we could try and figure out how to script it, for bonus points

# install BiocInstaller as biocbuild
# this will prompt for the biocbuild password;
# not sure if it can be made non-interactive
#iex "$r -e `"source('http://bioconductor.org/biocLite.R')`""
Start-Process $r -Credential biocbuild -ArgumentList "-e `"source('http://bioconductor.org/biocLite.R')`""

# useDevel() if appropriate; this will prompt (again?)
# for biocbuild's password
if ($env:USE_DEVEL -eq "TRUE") {Start-Process $r -Credential biocbuild -ArgumentList "-e BiocInstaller::useDevel()"}

# TODO (?) maybe all the stuff that needs to run as biocbuild
# could be put in its own script and that script could be run
# as biocbuild, so biocbuild's password only needs to be typed
# once.

# download + install MikTex
iex "$curl -LO http://mirrors.ctan.org/systems/win32/miktex/setup/basic-miktex-2.9.5105.exe"

iex ".\basic-miktex-2.9.5105.exe --unattended"

$path += ";C:\Program Files (x86)\MiKTeX 2.9\miktex\bin"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

[Environment]::SetEnvironmentVariable("MIKTEX_ENABLEWRITE18", "t", "Machine")

$wshell = New-Object -ComObject Wscript.Shell
$wshell.Popup("Manually set miktex settings (admin) to install needed pkgs on the fly w/o asking, and synchronize repositories.",0,"Done",0x1)


# java

# 32-bit

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/jdk-8u51-windows-i586.exe"

.\jdk-8u51-windows-i586.exe /s


$path +=  ";C:\Program Files (x86)\Java\jdk1.8.0_51\bin"

$path += ";C:\Program Files (x86)\Java\jdk1.8.0_51\jre\bin\server"


# 64-bit

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/jdk-8u51-windows-x64.exe"

.\jdk-8u51-windows-x64.exe /s

# java_home doesn't seem to matter
#[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk1.8.0_51", "Machine")

$path += ";C:\Program Files\Java\jdk1.8.0_51\bin"

# Also need to make sure jvm.dll is on path

# add stuff from both 32- and 64-bit sections to path:

$path += ";C:\Program Files\Java\jdk1.8.0_51\jre\bin\server"

[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path

# cygwin config

[Environment]::SetEnvironmentVariable("CYGWIN", "nodosfilewarning", "Machine")

## seems like javareconf is no longer necessary?
##Start-Process $r -Credential biocbuild -ArgumentList "CMD javareconf"

[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", $Env:GOOGLE_API_KEY, "Machine")

#### INSTALL SYSTEM DEPS

# ggobi

iex "$curl -LO http://www.ggobi.org/downloads/ggobi-2.1.10.exe"

# this automatically adds it to the path...
iex ".\ggobi-2.1.10.exe /S"

# ... so we need to get the path anew:

$path = [Environment]::GetEnvironmentVariable("PATH","Machine")


# FIXME - get ^^ to install w/o creating a desktop shortcut

# ...but we still need to do this:

[Environment]::SetEnvironmentVariable("GGOBI_HOME", "c:/progra~2/ggobi", "Machine")
[Environment]::SetEnvironmentVariable("GGOBI_PATH", "c:/progra~2/ggobi", "Machine")

# this is really useful for figuring out how to
# run various installers non-interactively:
# http://unattended.sourceforge.net/installers.php

# GTK+

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/gtk2.zip"

unzip .\gtk2.zip -d c:\

$path += ";C:\gtk2_2.22.1\bin"
$path += ";C:\gtk2_2.22.1_64bit\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

[Environment]::SetEnvironmentVariable("GTK_BASEPATH", "c:/GTK2_2~1.1", "Machine")


# gtkmm

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/gtkmm.zip"

unzip gtkmm.zip -d c:\

$path += ";c:\gtkmm\i386\bin;c:\gtkmm\x64\bin"

[Environment]::SetEnvironmentVariable("LIB_GTKMM", "c:/gtkmm", "Machine")

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# imagemagick

mkdir c:\ImageMagick

[Environment]::SetEnvironmentVariable("IM_BASEPATH", "c:/ImageMagick", "Machine")
[Environment]::SetEnvironmentVariable("LIB_IMAGEMAGICK", "c:/ImageMagick", "Machine")


# a. 32-bit

mkdir c:\ImageMagick\i386

iex "$curl -LO http://www.imagemagick.org/download/binaries/ImageMagick-6.9.1-10-Q16-x86-dll.exe"

# the noicons switch does not seem to work:
.\ImageMagick-6.9.1-10-Q16-x86-dll.exe /DIR=c:\ImageMagick\i386 /noicons /verysilent

$path += ";c:\ImageMagick\i386"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")



# b. 64-bit

mkdir c:\ImageMagick\x64

iex "$curl -LO http://www.imagemagick.org/download/binaries/ImageMagick-6.9.1-10-Q16-x64-dll.exe"

.\ImageMagick-6.9.1-10-Q16-x64-dll.exe /DIR=c:\ImageMagick\x64 /noicons /verysilent

$path += ";c:\ImageMagick\x64"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# JAGS

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/JAGS-3.4.0.exe"

.\JAGS-3.4.0.exe /S

[Environment]::SetEnvironmentVariable("JAGS_ROOT", "C:\Program Files\JAGS\JAGS-3.4.0", "Machine")

# boost

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/boost.zip"

unzip boost.zip -d c:\

[Environment]::SetEnvironmentVariable("LIB_BOOST", "c:/boost", "Machine")

# expat

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/expat.zip"

unzip .\expat.zip -d c:\

[Environment]::SetEnvironmentVariable("LIB_EXPAT", "c:/expat", "Machine")

# gsl

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/gsl.zip"

unzip .\gsl.zip -d c:\gsl

$path += ";c:\gsl\i386\bin;c:\gsl\x64\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")


[Environment]::SetEnvironmentVariable("LIB_GSL", "c:/gsl", "Machine")

# GTK - doesn't seem to be used?

# hdf5

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/hdf5.zip"

unzip .\hdf5.zip -d c:\hdf5

[Environment]::SetEnvironmentVariable("LIB_HDF5", "c:/hdf5", "Machine")

$path += ";c:\hdf5\i386\bin;c:\hdf6\x64\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# netcdf

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/netcdf.zip"

unzip .\netcdf.zip -d c:\netcdf

[Environment]::SetEnvironmentVariable("LIB_NETCDF", "c:/netcdf", "Machine")

$path += ";C:\netcdf\i386\bin;C:\netcdf\x64\bin;C:\netcdf\i386\deps\shared\bin;C:\netcdf\x64\deps\shared\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# protobuf

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/protobuf.zip"

unzip .\protobuf.zip -d c:\protobuf

[Environment]::SetEnvironmentVariable("LIB_PROTOBUF", "c:/protobuf", "Machine")

# libxml2

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/libxml2.zip"

unzip .\libxml2.zip -d c:\libxml2

[Environment]::SetEnvironmentVariable("LIB_XML2", "c:/libxml2", "Machine")

# libsbml

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/libsbml.zip"

unzip .\libsbml.zip -d c:\libsbml

[Environment]::SetEnvironmentVariable("LIBSBML_PATH", "c:/libsbml", "Machine")

# nlopt

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/nlopt.zip"

unzip .\nlopt.zip -d c:\nlopt

[Environment]::SetEnvironmentVariable("NLOPT_HOME", "c:/nlopt/2.2.3", "Machine")

# openbabel

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/openbabel.zip"

unzip .\openbabel.zip -d c:\

[Environment]::SetEnvironmentVariable("OPEN_BABEL_BIN", "c:/openbabel", "Machine")
[Environment]::SetEnvironmentVariable("OPEN_BABEL_SRC", "c:/openbabel_src", "Machine")


iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/OpenBabel2.3.2a_Windows_Installer.exe"


# oops, this seems to require interactivity:
.\OpenBabel2.3.2a_Windows_Installer.exe /S

[Environment]::SetEnvironmentVariable("OPEN_BABEL_INCDIR", "C:/openbabel_src/i386/include", "Machine")
[Environment]::SetEnvironmentVariable("OPEN_BABEL_LIBDIR", "c:/PROGRA~2/OPENBA~1.2", "Machine")

# no need to add to path, it adds it itself, but we need
# to re-get the path:

# the installer adds the openbabel path, but just 
# for the current user, but that's not enough, so we need
# to add it again (it will appear twice when echoing)
# the path but that's ok).

$path += ";C:\Program Files (x86)\OpenBabel-2.3.2"
[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")


# misc - (for gdsfmt) - why can't they use another way?

[Environment]::SetEnvironmentVariable("NUMBER_OF_PROCESSORS", "16", "Machine")

# postgresql

iex "$curl -LO https://s3.amazonaws.com/bioc-windows-setup/postgresql-9.1.1-1-windows.exe"

.\postgresql-9.1.1-1-windows.exe --mode unattended --superpassword $Env:POSTGRES_SUPERPASSWORD

[Environment]::SetEnvironmentVariable("PS_HOME", "C:\Program Files (x86)\PostgreSQL\9.1", "Machine")


# process explorer

iex "$curl -LO https://download.sysinternals.com/files/ProcessExplorer.zip"

unzip .\ProcessExplorer.zip -d C:\Windows



# root

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/root.zip"

unzip .\root.zip -d c:\root

[Environment]::SetEnvironmentVariable("ROOTSYS", "C:\root", "Machine")

$path += ";c:\root\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")


# ? need to add to LIB var? (see moscato1)
# well, let's just try it...

[Environment]::SetEnvironmentVariable("LIB", "c:\root\lib", "Machine")


# perl deps

# put perl on path inside powershell:

[Environment]::GetEnvironmentVariable("PATH","Machine")

ppm install DBD-mysql
ppm install Archive::Extract




# ensemblVEP

# this needs to be done as biocbuild, so here's a script to do so
# which must be run as biocbuild

# this line does not seem to work (at least now)
# for running the script as biocbuild, but you can manually
# do so, just log in as biocbuild and run the script
# at the powershell prompt.
Start-Process "c:\biocbld\BBS\utils\setup-vep.ps1" -Credential biocbuild




cd $download_dir

[Environment]::SetEnvironmentVariable("VEP_PATH", "c:\vep\variant_effect_predictor.pl", "Machine")

$path += ";c:\vep"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# misc

[Environment]::SetEnvironmentVariable("SWEAVE_STYLE", "TRUE", "Machine")

# TEMP and TMP do have values already; should we overwrite them?
#[Environment]::SetEnvironmentVariable("TEMP", "c:\Windows\TEMP", "Machine")
#[Environment]::SetEnvironmentVariable("TMP", "c:\Windows\TEMP", "Machine")

# msvc runtimes

# x86
iex "$curl -LO http://download.microsoft.com/download/5/B/C/5BC5DBB3-652D-4DCE-B14A-475AB85EEF6E/vcredist_x86.exe"

.\vcredist_x86.exe /q

# x64
iex "$curl -LO http://download.microsoft.com/download/3/2/2/3224B87F-CFA0-4E70-BDA3-3DE650EFEBA5/vcredist_x64.exe"


# mpi stuff

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/MSMPISetup.exe"

# Note, this puts its directory at the BEGINNING of the path....
# should probably fix that.
.\MSMPISetup.exe -unattend


iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/mpich2.zip"

unzip .\mpich2.zip -d c:\mpich2

$path += ";C:\mpich2\i386\bin;C:\mpich2\x64\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# graphviz

iex "$curl -LO http://www.graphviz.org/pub/graphviz/stable/windows/graphviz-2.38.msi"

 .\graphviz-2.38.msi /quiet

$path += ";C:\Program Files (x86)\Graphviz2.38\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# ipython

C:\Python27\Scripts\pypm.exe install ipython

# jupyter

# FIXME!

# pandoc

iex "$curl -LO https://github.com/jgm/pandoc/releases/download/1.13.2/pandoc-1.13.2-windows.msi"

.\pandoc-1.13.2-windows.msi /quiet ALLUSERS=1

$path += ";C:\Program Files (x86)\Pandoc"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# ghostscript

iex "$curl -LO http://downloads.ghostscript.com/public/gs916w32.exe"

.\gs916w32.exe /S

$path += ";C:\Program Files (x86)\gs\gs9.16\bin"

# clustal omega (clustalo)

iex "$curl -LO http://www.clustal.org/omega/clustal-omega-1.2.0-win32.zip"

unzip -j .\clustal-omega-1.2.0-win32.zip -d c:\clustalo

$path += ";c:\clustalo"

