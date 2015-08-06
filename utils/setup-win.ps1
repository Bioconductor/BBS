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

mkdir $bioc_basedir

cd $bioc_basedir

mkdir log
# need to create NodeInfo dir as biocbuild:
Start-Process mkdir -Credential biocbuild -ArgumentList "$bioc_basedir\NodeInfo"

# BTW, sometimes the Start-Process line fails with 
# an error about an invalid directory. The solution
# is to close the powershell window and open a new one.




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


iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/jdk-8u51-windows-x64.exe"

.\jdk-8u51-windows-x64.exe /s

[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Java\jdk1.8.0_51", "Machine")

$path += ";C:\Program Files\Java\jdk1.8.0_51\bin"


[Environment]::SetEnvironmentVariable("PATH", $path, "Machine")

# set it locally so we don't have to wait for a restart:
$Env:Path = $path


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

# a. 32 bit

iex "$curl -LO http://win32builder.gnome.org/packages/3.6/gtk+_3.6.4-1_win32.zip"

unzip gtk+_3.6.4-1_win32.zip -d c:\gtk+_3.6.4-1

[Environment]::SetEnvironmentVariable("GTK_BASEPATH", "c:/gtk__3~1.4-1", "Machine")

$path += ";C:\gtk+_3.6.4-1\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# b. 64-bit

iex "$curl -LO http://win32builder.gnome.org/packages/3.6/gtk+_3.6.4-1_win64.zip"

unzip gtk+_3.6.4-1_win64.zip -d c:\gtk+_3.6.4-1_64bit

$path += ";C:\gtk+_3.6.4-1_64bit\bin"

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")

# gtkmm

iex "$curl -LO http://s3.amazonaws.com/bioc-windows-setup/gtkmm.zip"

unzip gtkmm.zip -d c:\gtkmm

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




# root
# ? need to add to LIB var? (see moscato1)
