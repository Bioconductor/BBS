# How to set up a Mac OS X Host with Parallels Desktop

This document describes how to install Parallels Desktop on a Mac Pro and
configure a virtual machine running El Capitan OS X 10.11.6.

Table of Contents:
===================

- [Terminology and Documentation](#terminology)
- [Host](#host)
  - [User Accounts](#host-user-accounts) 
  - [Hostname](#host-hostname) 
  - [Network](#host-network) 
  - [Power management settings](#host-power-management)
  - [Enable SSH](#host-ssh) 
  - [Install Xcode](#host-xcode) 
  - [Parallels Desktop](#host-parallels) 
    - [Install](#parallels-install) 
    - [Create a boot Image](#parallels-create-boot-image) 
    - [Configure and create the VM](#parallels-configure-and-create) 
- [Guest](#guest)
  - [Install Parallels Tools](#guest-parallels-tools)
  - [Power management settings](#guest-power-management)

<a name="terminology"></a>
## Terminology and Documentation 
---------------------------------------------

* Terminology

The 'Host' refers to the Mac Pro machine running as the hypervisor. At the time
this was written, the Host was running Mojave 10.14.1.

The 'Guest' refers to the virtual machine running on the Host, managed by
Parallels Desktop. The OS X to be installed on the Guest is El Capitan 10.11.6.

Parallels Desktop 14 for Mac Business Edition (14.1.0) was used to configure
this VM. The licence was purchased Oct 14, 2018 and is good for one year
(expires Oct 14, 2019).

* Parallels Desktop documentation 

[Parallels Desktop Business Edition Reference](https://download.parallels.com/desktop/v10/docs/en_US/Parallels%20Desktop%20Business%20Edition%20Administrator's%20Guide.pdf)

There are 2 command line utilities worth noting, `prlsrvctl` and `prlctl`. 

`prlsrvctl` is used to administer the Parallels Desktop. Tasks that can be
performed include (but are not limited to) getting configuration settings,
modifying preferences, getting a list of users, obtaining statistics and
installing a license. 

`prlctl` is used to perform administrative tasks on virtual machines. The
utility supports creating and administering virtual machines, installing
Parallels Tools, getting statistics, and generating problem reports.

* Mac OS X CLI documentation

[Mac OS X Server Command-Line Administration](https://www.apple.com/server/docs/Command_Line.pdf)


These instructions assume a pristine Mac Pro with no existing user accounts. Connect a monitor and start the machine ...

<a name="host"></a>
## Host
---------------------------------------------

<a name="host-user-accounts"></a>
### User Accounts 

The Host should have an `administrator` account and 1 or 2 other Admin users.
Order of creation doesn't matter. `administrator` is the user that Parallels
will run as. The other Admin accounts serve as a backups that can sudo to
`administrator` in the case of a lost password, account corruption etc.

i) Create your personal account:

As part of the set-up process, there will be a prompt to create the first user
account. By default this account will be in the Admin group. Here I created my
personal account `vobencha`.

ii) Create `administrator` and other Admin users:

From your personal account, create the `administrator` account and one other
Admin user.

  - Open 'System Preferences'
  - Go to 'Users and Groups'
  - Unlock to make changes
  - Add the new account
  - Click 'Allow user to administer this computer'

Add the password for the `administrator` user to the Google Credentials doc.

iii) Public keys

Install the appropriate devteam member public keys in the `administrator`
account.

This account should not be confused with the `administrator` user on the VM
which is accessible by all devteam members. The `administrator` account on the
host (macHV2) is the account that creates, runs and destroys the VM and should
have limited access.

    TESTING: Logout and try to login again as administrator. 

Install the appropriate personal public keys in the personal accounts created.

The remainder of the set-up should be performed as the `administrator` user.

<a name="host-hostname"></a>
### Hostname
---------------------------------------------

Set the hostname to `macHV2` to represent the hypervisor for the 2-series builds.

From a terminal window:

    sudo scutil --set ComputerName macHV2
    sudo scutil --set LocalHostName macHV2
    sudo scutil --set HostName macHV2.bioconductor.org

  TESTING:

    scutil --get ComputerName
    scutil --get LocalHostName
    scutil --get HostName
    networksetup -getcomputername

<a name="host-network"></a>
### Network
---------------------------------------------

There are 2 physical ports on the Mac Pro. We'll use port 1 (Ethernet 1) for the Host, macHV2
and port 2 (Ethernet 2) for the Guest, celaya2.

* Some userful commands

List network services:

    sudo networksetup -listallhardwareports
    sudo networksetup -listallnetworkservices

* Assign static IP (override DHCP):

The IP, subnet and router information came from RPCI. 

    # sudo networksetup -setmanual SERVICE IP SUBNET ROUTER
  Val home network:
    sudo networksetup -setmanual 'Ethernet 1' 192.168.1.101 255.255.255.0 192.168.1.1

  RPCI network:
    sudo networksetup -setmanual 'Ethernet 1' 192.168.1.101 255.255.255.0 192.168.1.1

  TESTING:

    sudo ifconfig

To clear the setting and go back to DHCP if necessary:

    sudo systemsetup -setdhcp 'Ethernet 1'

* Assign DNS servers:

  Val home network:
    sudo networksetup -setdnsservers 'Ethernet 1' 192.168.1.1 8.8.8.8
    sudo networksetup -setsearchdomains 'Ethernet 1' robench.org

  RPCI network:
    #sudo networksetup -setdnsservers 'Ethernet 1' 216.126.35.8 216.24.175.3 8.8.8.8
    #sudo networksetup -setsearchdomains 'Ethernet 1' bioconductor.org

  TESTING:

    networksetup -getdnsservers 'Ethernet 1'
    ping www.bioconductor.org

** Apply all software updates and reboot

    softwareupdate -l         # list all software updates
    sudo softwareupdate -ia   # install them all (if appropriate)
    sudo reboot               # reboot

<a name="host-power-management"></a>
### Power management settings
---------------------------------------------

* Prevent the Host from sleeping and enable auto-restart:

`pmset` manages power management settings such as idle sleep timing, wake on
access, automatic restart on power loss etc. Set `displaysleep`, `disksleep`
and `sleep` to zero (FALSE) and `autorestart` to one (TRUE):

    sudo pmset -a displaysleep 0 disksleep 0 sleep 0 autorestart 1

To list all power management capabilities:

    macHV2:CommandLineTools administrator$ pmset -g cap
    Capabilities for AC Power:
     displaysleep
     disksleep
     sleep
     womp
     autorestart
     gpuswitch
     standby
     standbydelayhigh
     standbydelaylow
     highstandbythreshold
     powernap
     ttyskeepawake
     hibernatemode
     hibernatefile
     autopoweroff
     autopoweroffdelay

To list all power management capabilities in use:

    macHV2:CommandLineTools administrator$ pmset -g
    System-wide power settings:
    Currently in use:
     standby              1
     Sleep On Power Button 1
     womp                 1
     autorestart          1
     hibernatefile        /var/vm/sleepimage
     powernap             1
     gpuswitch            2
     networkoversleep     0
     disksleep            0
     standbydelayhigh     86400
     sleep                0
     autopoweroffdelay    28800
     hibernatemode        0
     autopoweroff         1
     ttyskeepawake        1
     displaysleep         0
     highstandbythreshold 50
     standbydelaylow      86400

<a name="host-ssh"></a>
### Enable SSH
---------------------------------------------

* Enable SSH:

Remote login will be set to 'off':

    sudo systemsetup -getremotelogin

Set to 'on' and confirm the change:

    sudo systemsetup -setremotelogin on
    sudo systemsetup -getremotelogin
    
* Confirm remote events are off:

    sudo systemsetup -getremoteappleevents
    sudo systemsetup -setremoteappleevents off

<a name="host-xcode"></a>
### Install Xcode
---------------------------------------------

* FIXME

Should we install Xcode on the Host ...?

<a name="host-parallels"></a>
### Parallels Desktop 
---------------------------------------------

<a name="parallels-install"></a>
#### Install

Parallels Desktop 14 for Mac Business Edition (14.1.0) was used to configure
this VM. The licence was purchased Oct 14, 2018 and is good for one year
(expires Oct 14, 2019).

As the `administrator` user ...

* Purchase and download Parallels Desktop for Business from the Apple Store.

* Register the licence.

Each licence can be installed on one machine only.

* Choose a default location for VM files:

Go to Preferences -> Virtual machine folder and set this field:

    Virtual machines folder: /Users/administrator/parallels

NOTE: To share VMs across user accounts, the VM files must be in a shared
location with the appropriate permissions. When a VM is shared from
one user to another it must be temporarily suspended before the next user can
access it. This type of sharing isn't applicable to our situation. The
VMs will only be run as the `administrator` user so, for now at least, the
VM files will be in the `administrator` home directory.

* Disable automatic updates

Go to Preferences -> Virtual machine folder and set these fields:

    Check for updates: Never
    Unclick 'Download updates automatically'

Updates should be run manually or scheduled at a known time. Automatic
updates can cause unexpected problems that are difficult to track down.

<a name="parallels-el-capitan-files"></a>
#### Prepare El Capitan files
---------------------------------------------

The El Capitan files are on a UBS key purchased from Amazon.

* Insert the USB key

* View the contents in /Volumes

    macHV2:~ administrator$ ls -l /Volumes/
    total 0
    lrwxr-xr-x   1 root           wheel    1 Nov 22 15:37 Macintosh HD -> /
    drwxrwxr-x@ 21 administrator  staff  782 Jan  1  2016 OS X 10.11 Install Disk - 10.11.6
    
    cd /Volumes/OS X 10.11 Install Disk - 10.11.6
     
    macHV2:~ administrator$ ls -l /Volumes/OS\ X\ 10.11\ Install\ Disk\ -\ 10.11.6/
    total 72
    -rw-r--r--@ 1 administrator  staff  34542 Jul 18 07:14 ElCapitanBackground.png
    drwxr-xr-x  3 administrator  staff    102 Aug 31  2016 Install OS X El Capitan.app
    drwxr-xr-x@ 3 administrator  staff    102 Jul 18 07:14 Library
    drwxr-xr-x@ 3 administrator  staff    102 Jul 18 07:14 System
    drwxr-xr-x+ 9 administrator  staff    306 Jul 18 07:14 Utilities
    -rw-r--r--@ 1 administrator  staff      0 Jul 18 07:14 mach_kernel
    drwxr-xr-x@ 3 administrator  staff    102 Jul 18 07:14 usr

* Make a backup of the USB files

    cd /Users/administrator/Parallels
    mkdir el-capitan-usb-backup 

The .app directory is the important one but we'll make a full copy of the USB:

    cd /Volumes
    macHV2:Volumes administrator$ ls
    Macintosh HD                      OS X 10.11 Install Disk - 10.11.6
    macHV2:Volumes administrator$ cp -r OS\ X\ 10.11\ Install\ Disk\ -\ 10.11.6 /Users/administrator/Parallels/el-capitan-usb-backup/
    cp: OS X 10.11 Install Disk - 10.11.6/.Spotlight-V100: unable to copy extended attributes to /Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/.Spotlight-V100: Operation not permitted
    cp: OS X 10.11 Install Disk - 10.11.6/.Spotlight-V100: Operation not permitted
    cp: OS X 10.11 Install Disk - 10.11.6/.Trashes: unable to copy extended attributes to /Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/.Trashes: Permission denied
    cp: OS X 10.11 Install Disk - 10.11.6/.Trashes: Permission denied

This takes some time. Total size is ~ 6 GB.

    macHV2:Parallels administrator$ du -hs /Users/administrator/Parallels/el-capitan-usb-backup/OS\ X\ 10.11\ Install\ Disk\ -\ 10.11.6/*
     36K	/Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/ElCapitanBackground.png
    5.8G	/Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/Install OS X El Capitan.app
    4.0K	/Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/Library
     22M	/Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/System
     21M	/Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/Utilities
      0B	/Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/mach_kernel
    592K	/Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/usr

<a name="parallels-create-boot-image"></a>
#### Create a boot image 

Next Parallels will make a bootable image file (.hdd) from the files in the .app directory.

* Click on the Parallels desktop Icon to bring up the Installation Assistant. Skip
the Windows installation if it prompts for one.

* Click on 'Install Windows or another OS from a DVD or image file' 
 -> Choose manually
 -> Select a file ...

* Under 'Locations' choose OSX 10.11 Install Disk
  -> remove file filters so all files are select-able
  -> select Install OS X El Capitan

* Parallels will prompt that it needs to make a bootable disk image file.
  Click 'Continue'. Name the image ElCapitan-bootable-image-<date> and
  save the file to /Users/administrator/Parallels.

Once the bootable image is made you can continue with configuration
and installation or do it later. The output of this step is the
/Users/administrator/Parallels/ElCapitan-bootable-image-<date>.hdd file
that can be used to configure new VMs.

* Remove the USB key

Using the Finder or the desktop icon, eject the USB and then physically remove
it from the machine. This step prevents accidental writes to the USB
key in future steps.

<a name="parallels-configure-and-create"></a>
#### Configure and create the VM

Click on the Parallels Desktop icon
  -> Create new VM
  -> Install Windows or another OS froma  DVD or image file
  -> Choose manually
  -> Select a file ...

Remove file filters so all files are select-able
  -> choose /Users/administrator/Parallels/ElCapitan-bootable-image-<date>.hdd

A page will come up with 'Unable to detect operating system'
  -> Continue
  -> Select operating system 'macOS'
  -> Name the VM (celaya2 in this case)
  -> Save in /Users/administrator/Parallels
  -> Unclick 'Create alias on Mac desktop'
  -> Click 'Customize setting before installation'
  -> Click 'Create'

* Customize settings:

i) General tab 

No change.

ii) Options tab

Startup and Shutdown: 
  Select 'Custom'
    Start Automatically: When Mac starts
    On Window Close: Keep running in background
  Leave the other defaults

Sharing:
  Unclick 'Share cloud folders with virtual machine'
  Unclick 'Map Mac volumes to virtual machine'

More Options:
  Unclick 'Update Parallels Tools automatically'

Leave all other defaults.

iii) Hardware tab

CPU and Memory:
  Set processors to 23 (we have 12 real; 24 virtual total)
  Set Memory to 58000 MB
    Parallels has a limit on the amount of memory it wants to allocate per VM
    based on the memory of the Host. This Mac Pro has 64 GB RAM and it seems
    Parallels doesn't want to allocate more than 57-58 GB. If a warning pops up
    suggesting the optimal memory range, allow it to optimize by clicking 'change'
    and you'll end up around 57252 MB.
  Keep all defaults in 'Advanced Settings'

Network:
TODO

Hard Disk 1:
  Advanced Settings -> properties 
    Increase disk size to 800 GB
    Do NOT select 'Split the disk image into 2 GB files'
    Leave 'Expanding disk' checked
    Click 'Apply'

Hard Disk 2:
  This is the bootable image (.hdd) we are using to launch the VM.
  Leave it as is.

iv) Security tab 

No change.

v) Backup tab

No change.


* Close the configuration window and click 'Continue'.

* Ignore prompts (i.e., click 'Close') for access to the camera and microphone.

* Machine will boot

A screen will come up prompting the set up the installation of OS X:

-> click continue
-> accept terms

A screen will come up asking which disk on which to install OS X: 

-> Choose 'Macintosh HD'

NOTE:  The other option here is 'Install OS X El Capitan'. That is the bootable disk image (.hdd) we 
used to create the VM. Do not select this.

* Installation takes about 13 minutes

* Set up

A series of set-up screens will come up:

- Choose the country
- Choose the keyboard configuration
- Transfer Information to This Mac 
  -> Don't transfer any information now
- Enable Location Services
  -> Do not enable this (default is unselected)
- Don't sign in with your Apple ID
- Agree to terms and conditions
- When prompted to create a user account, create `administrator`.
Use the same `administrator` password as the other build machines and record this in the Google Credentials doc.
- Select New York EST time zone
- Diagnositcs & Usage
  -> Deselect 'Send diagnostics & usage data to Apple'
  -> Deselect 'Share crash data with app developers'

* Detach boot image file

Once set up is complete, detach the boot image file. This image can be used to launch
new VMs so don't put it in the trash (last step).

- Stop the VM
  Go to Parallels -> Control Center. Select celaya2 -> Actions -> Stop.
- Select the gear icon in celaya2. 
- Select the Hardware tab -> Hard Disk 2
- The .hdd file should be listed in the 'Source' field
- Unlock the settings if locked
- Disconnect .hdd file by clicking the minus '-'
- Select 'Keep files'. Don't move them to the trash.

* Status check

From a terminal on the Host, check the status of the VM:

    prlctl list -i


<a name="guest"></a>
## Guest 
---------------------------------------------

<a name="guest-parallels-tools"></a>
## Install Parallels Tools

* Install Parallels Tools

Parallels Tools is a suite of utilities (drivers) that help the VM communicate
more efficiently with the Host. All utilities supported by the guest OS are
installed in the VM as a single package when Parallels Tools is installed.

Parallels Tools are located on disk images that are installed with Parallels
Desktop. There is a separate image for each supported guest OS, located here:

macHV2:~ administrator$ ls -l /Applications/Parallels\ Desktop.app/Contents/Resources/Tools/
total 299088
-rw-r--r--  1 root  wheel       802 Nov 14 16:03 Autounattend.vbs
-rw-r--r--  1 root  wheel     17634 Nov 14 16:03 Autounattend.xml
-rw-r--r--  1 root  wheel   9494664 Nov 14 16:03 PTIAgent.exe
-rw-r--r--  1 root  wheel     90248 Nov 14 16:03 igt.exe
-rw-r--r--  1 root  wheel  68413440 Nov 14 16:03 prl-tools-lin.iso
-rw-r--r--  1 root  wheel  29208576 Nov 14 16:03 prl-tools-mac.iso
-rw-r--r--  1 root  wheel   9873408 Nov 14 16:03 prl-tools-win.iso
-rw-r--r--  1 root  wheel  36015745 Nov 14 16:03 prl-tools-win.tar.gz
drwxrwxr-x  6 root  wheel       192 Nov 14 16:03 prl_tg

Start the VM by going to Parallels -> Control Center. Select celaya -> Actions -> Start.
- Click on the yellow triangle with exclaimation point at the top right of the menu bar.
- Follow the prompts to install Parallels Tools.
- Installation requires a reboot of the VM. When the prompt comes up, click 'restart'.
- If a 'Parallels Tools' icon was left on the VM desktop, click on the icon and eject the disk.

Alternatively, the tools can be installed on the Guest from a terminal window on the Host
using the `prlctl` command:

    prlctl installtools celaya2

<a name="guest-power-management"></a>
## Power Management settings

This command is run from the terminal on the Host (no sudo needed). It instructs
Parallels to start the VM when the host starts up, i.e., on reboot, prevents pause
when idle or when windows close. 

    prlctl set celaya2 --autostart start-host --pause-idle off --on-window-close keep-running

Prioritize Guest over Host?

    prlctl set celays2 --faster-vm on

This command is run from a terminal window inside the VM:

Prevent the Host from sleeping and enable auto-restart:

    sudo pmset -a displaysleep 0 disksleep 0 sleep 0 autorestart 1

<a name="guest-ssh"></a>
## Enable SSH 

Open a terminal window in the VM. By default, 'remotelogin' is set to 'off'. Set it to 'on':

    celaya2:~ administrator$ sudo systemsetup -getremotelogin
    Remote Login: Off
    celaya2:~ administrator$ sudo systemsetup -setremotelogin on

Confirm remote events are off:

    celaya2:~ administrator$ sudo systemsetup -getremotelogin
    Remote Login: On

Confirm remote apple events are off:

These should be off by default.

    celaya2:~ administrator$ sudo systemsetup -getremoteappleevents
    Remote Apple Events: Off


<a name="guest-user-accounts"></a>
## User accounts 

When fully configured as a build machine, the VM will have 3 users: administrator, biocbuild
and pkgbuild. This could be done as part of the next HOWTO but it is straightforward to 
create these now when you have the monitor hooked up.

Go to System Preferences -> Users and Groups:
- Create a `biocbuild` account with Admin prividledges.
- Create a `pkgbuild` account with Standard priviledges. 

From a terminal window in either the Host or Guest, add the approprate SSH keys
to the admin, biocbuild and pkgbuild users. Record who is in what group in the
Google Credentials Doc.

<a name="guest-hostname"></a>
### Hostname
---------------------------------------------

Set the hostname to `celaya2`.

From a terminal window:

    sudo scutil --set ComputerName celaya2 
    sudo scutil --set LocalHostName celaya2 
    sudo scutil --set HostName celaya2.bioconductor.org

  TESTING:

    scutil --get ComputerName
    scutil --get LocalHostName
    scutil --get HostName
    networksetup -getcomputername

* Restart the VM

<a name="guest-network"></a>
### Network
---------------------------------------------

* Bridge networking 

Bridge networking allows the VM to access the local network and Internet
through one of the network adapters installed on the Host. The VM Guest will be
treated as an independent computer on the network instead of sharing the same
network connection as the Host.  

There are 2 physical ports on the Mac Pro. The first port (Ethernet 1) is used
for the Host, macHV2, and the second (Ethernet 2) will be used for the Guest,
celaya2. Configuration can be done from the GUI in the running VM or from a terminal in the Host.

-- Option 1: From the VM Guest

Start the VM if not running.

From within the celaya2 VM, click on the gear icon and the 'hardware' tab. Select 
'Networking'. Under 'Source' select 'Ethernet 2'

Leave the Network Conditioner unselected. Keep all other defaults. 

-- Option 2: From a terminal on the Host

We need to get the name of the physical adapter on the Mac Pro that the VM adapter will be bridged to.

List the network adapters associated with the virtual networks:

    macHV2:Library administrator$ networksetup listnetworkserviceorder
    An asterisk (*) denotes that a network service is disabled.
    (1) Ethernet 1
    (Hardware Port: Ethernet 1, Device: en0)
    
    (2) Ethernet 2
    (Hardware Port: Ethernet 2, Device: en1)
    
    (3) Wi-Fi
    (Hardware Port: Wi-Fi, Device: en2)
    
    (4) Bluetooth PAN
    (Hardware Port: Bluetooth PAN, Device: en9)
    
    (5) Thunderbolt Bridge
    (Hardware Port: Thunderbolt Bridge, Device: bridge0)

A simliar (sometimes useful) command with 'Type' included:

    macHV2:Library administrator$ prlsrvctl net list
    Network ID        Type      Bound To
    Shared            shared  vnic0 
    NAT server:
    
    Host-Only         host-only  vnic1
    Ethernet 1 (en0)  bridged   en0
    Ethernet 2 (en1)  bridged   en1
    Wi-Fi (en2)       bridged   en2
    vnic0 (vnic0)     bridged   vnic0
    vnic1 (vnic1)     bridged   vnic1
    Default           bridged   FF:FF:FF:FF:FF:FF

The Host is using Ethernet 1 (en0) and the Guest will use Ethernet 2 (en1).
The output above shows the 'Ethernet 2 (en1)' virtual network is attached to
the 'en1' physical adapter.

To connect the VM to the 'Ethernet 2 (en1)' network we need to know the name of
the network adapter on the VM.  Use `prlctl list` to see the networking on the
VM. 

This output was truncated but the important thing to note is the networking on 'net0'
adapter of the VM. By default it will say 'shared': 

    macHV2:Library administrator$ prlctl list celaya2 -i
    INFO
    ID: {1652f656-55be-4fc6-9078-a6260b8fd095}
    Name: celaya2
    Description: 
    Type: VM
    State: running
    OS: macosx
    ...
    Hardware:
      cpu cpus=23 VT-x accl=high mode=32
      memory 57252Mb
      video 64Mb 3d acceleration=highest vertical sync=yes high resolution=no automatic video memory=no
      memory_quota auto
      hdd0 (+) sata:0 image='/Users/administrator/Parallels/celaya2.pvm/celaya2-0.hdd' type='expanded' 819200Mb online compact=on
      cdrom0 (+) sata:1 image='/Applications/Parallels Desktop.app//Contents/Resources/Tools/prl-tools-mac.iso' state=disconnected
      usb (+)
      net0 (+) type=shared mac=001C42B43DED card=e1000
      sound0 (+) output='Default' mixer='Mute'
    ...

Stop the VM:

    prlctl stop celaya2

Attach the net0 network adapter in the Guest to the en1 adapter in the Host:

    macHV2:Library administrator$ prlctl set celaya2 --device-set net0 --type bridged --iface en1
    Configure net0 (+) type=bridged iface='Ethernet 2' mac=001C42B43DED card=e1000
    
    Configured net0 (+) type=bridged iface='Ethernet 2' mac=001C42B43DED card=e1000
    
    
    The VM has been successfully configured.

Confirm net0 is bridged to en1:

    macHV2:Library administrator$ prlctl list celaya2 -i
    INFO
    ID: {1652f656-55be-4fc6-9078-a6260b8fd095}
    Name: celaya2
    Description: 
    Type: VM
    State: stopped
    OS: macosx
    ...
    Hardware:
      cpu cpus=23 VT-x accl=high mode=32
      memory 57252Mb
      video 64Mb 3d acceleration=highest vertical sync=yes high resolution=no automatic video memory=no
      memory_quota auto
      hdd0 (+) sata:0 image='/Users/administrator/Parallels/celaya2.pvm/celaya2-0.hdd' type='expanded' 819200Mb online compact=on
      cdrom0 (+) sata:1 image='/Applications/Parallels Desktop.app//Contents/Resources/Tools/prl-tools-mac.iso' state=disconnected
      usb (+)
      net0 (+) type=bridged iface='Ethernet 2' mac=001C42B43DED card=e1000
      sound0 (+) output='Default' mixer='Mute'
      ...

* Assign static IP:

The IP, subnet and router information came from RPCI. 

Query VM for network adapter name:

    celaya2:~ administrator$ networksetup -listnetworkserviceorder
    An asterisk (*) denotes that a network service is disabled.
    (1) Ethernet
    (Hardware Port: Ethernet, Device: en0)

Set the static IP, subnet mask and router:

    # sudo networksetup -setmanual SERVICE IP SUBNET ROUTER
    # if Val home network:
    sudo networksetup -setmanual 'Ethernet' 192.168.1.102 255.255.255.0 192.168.1.1
    # else if RPCI network:
    sudo networksetup -setmanual 'Ethernet 1' 192.168.1.101 255.255.255.0 192.168.1.1

  TESTING:

    sudo ifconfig

* Assign DNS servers:

    # if Val home network:
    sudo networksetup -setdnsservers 'Ethernet' 192.168.1.1 8.8.8.8
    sudo networksetup -setsearchdomains 'Ethernet' robench.org
    # else if RPCI network:
    #sudo networksetup -setdnsservers 'Ethernet 1' 216.126.35.8 216.24.175.3 8.8.8.8
    #sudo networksetup -setsearchdomains 'Ethernet 1' bioconductor.org

  TESTING:

    networksetup -getdnsservers 'Ethernet'
    ping celaya2.bioconductor.org

** Apply all software updates and reboot

    softwareupdate -l         # list all software updates
    sudo softwareupdate -ia   # install them all (if appropriate)
    sudo reboot               # reboot

------------------------------------------------------------------------------

If Parallels is already installed and configured, go to the
[Prepare-Mac-OSX-El-Capitan-HOWTO.TXT](https://github.com/Bioconductor/BBS/blob/master/Doc/Prepare-MacOSX-El-Capitan-HOWTO.TXT). 
