<#
prerequisites:
a windows server 2012 r2 machine with
cygwin installed, specifically rsync, curl, and ssh
(and optionally vim) and in the path

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

[Environment]::SetEnvironmentVariable("PATH", "$path", "Machine")
