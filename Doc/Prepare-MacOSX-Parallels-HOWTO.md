# How to set up a Mac OS X Host with Parallels Desktop

This document describes how to install Parallels Desktop on a Mac Pro and
configure a virtual machine running El Capitan OS X 10.11.6.

Table of Contents:
===================

- [Terminology and References](#terminology)
- [Host](#host)
  - [User Accounts](#host-user-accounts) 
  - [Hostname](#host-hostname) 
  - [Network](#host-network) 
  - [Firewall](#host-firewall) 
  - [Power Management Settings](#host-power-management)
  - [Enable SSH](#host-ssh) 
  - [Remote Events and Timezone](#host-remote-events) 
  - [Parallels Desktop](#host-parallels) 
    - [Install](#parallels-install) 
    - [Create a boot Image](#parallels-create-boot-image) 
    - [Configure and create the VM](#parallels-configure-and-create) 
- [Guest](#guest)
  - [Install Parallels Tools](#guest-parallels-tools)
  - [User Accounts](#guest-user-accounts) 
  - [Hostname](#guest-hostname) 
  - [Network](#guest-network) 
  - [Firewall](#guest-firewall) 
  - [Power Management Settings](#guest-power-management)
  - [Enable SSH](#host-ssh) 
  - [Remote Events and Timezone](#guest-remote-events) 
  - [Disable System Integrity Protection (SIP)](#guest-disable-sip) 
- [Configure VM Guest as build machine](#configure-vm-guest-as-build-machine)

<a name="terminology"></a>
## Terminology and References 
---------------------------------------------

### Terminology

The 'Host' refers to the Mac Pro machine running as the hypervisor. At the time
this was written, the Host was running Mojave 10.14.1.

The 'Guest' refers to the virtual machine running on the Host, managed by
Parallels Desktop. The OS X to be installed on the Guest is El Capitan 10.11.6.

Parallels Desktop 14 for Mac Business Edition (14.1.0) was used to configure
this VM. The licence was purchased Oct 14, 2018 and is good for one year
(expires Oct 14, 2019).

### Parallels Desktop documentation 

[Parallels Desktop Business Edition Reference](https://download.parallels.com/desktop/v10/docs/en_US/Parallels%20Desktop%20Business%20Edition%20Administrator's%20Guide.pdf)

There are 2 command line utilities worth noting, `prlsrvctl` and `prlctl`. 

`prlsrvctl` is used to administer the Parallels Desktop. Tasks that can be
performed include (but are not limited to) getting configuration settings,
modifying preferences, getting a list of users, obtaining statistics and
installing a license. 

`prlctl` is used to perform administrative tasks on virtual machines. The
utility supports creating and administering virtual machines, installing
Parallels Tools, getting statistics, and generating problem reports.

### Mac OS X CLI documentation

[Mac OS X Server Command-Line Administration](https://www.apple.com/server/docs/Command_Line.pdf)

<a name="host"></a>
## Host
---------------------------------------------

These instructions assume a pristine Mac Pro with no existing user accounts.
A monitor is necessary to create the initial user accounts and it's
useful for most other actions documented here. 

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
host (machv2) is the account that creates, runs and destroys the VM and should
have limited access.

Testing: 

    Logout and try to login again as administrator. 

Install the appropriate personal public keys in the personal accounts created.

The remainder of the set-up should be performed as the `administrator` user.

<a name="host-hostname"></a>
### Hostname

Set the hostname to `machv2` to represent the hypervisor for the 2-series builds.

From a terminal window:

    sudo scutil --set ComputerName machv2
    sudo scutil --set LocalHostName machv2
    sudo scutil --set HostName machv2.bioconductor.org

Testing:

    scutil --get ComputerName
    scutil --get LocalHostName
    scutil --get HostName
    networksetup -getcomputername

<a name="host-network"></a>
### Network

There are 2 physical ports on the Mac Pro. We'll use port 1 (Ethernet 1) for
the Host, machv2 and port 2 (Ethernet 2) for the Guest, celaya2.

Open a terminal window on the VM.

List Host network services:

    sudo networksetup -listallhardwareports
    sudo networksetup -listallnetworkservices

 sudo networksetup -listallnetworkservices

i) Disable Wi-Fi, Bluetooth PAN and Thunderbolt Bridge services

By default all services are enabled:

    machv2:~ administrator$  sudo networksetup -listallnetworkservices
    Password:
    An asterisk (*) denotes that a network service is disabled.
    Ethernet 1
    Ethernet 2
    Wi-Fi
    Bluetooth PAN
    Thunderbolt Bridge

Disable Wi-Fi, Bluetooth PAN and Thunderbolt Bridge:

    machv2:~ administrator$  sudo networksetup -setnetworkserviceenabled Wi-Fi off 
    machv2:~ administrator$  sudo networksetup -setnetworkserviceenabled 'Bluetooth PAN' off
    machv2:~ administrator$  sudo networksetup -setnetworkserviceenabled 'Thunderbolt Bridge' off

Confirm:

    macHV2:~ administrator$  sudo networksetup -listallnetworkservices
    Password:
    An asterisk (*) denotes that a network service is disabled.
    Ethernet 1
    Ethernet 2
    *Wi-Fi
    *Bluetooth PAN
    *Thunderbolt Bridge

ii) Order network services

Ethernet 1 should have priority:

    sudo networksetup -listnetworkserviceorder
    sudo -ordernetworkservices 'Ethernet 1' 'Ethernet 2'

If Ethernet 1 is not first, then order and confirm:

    sudo -ordernetworkservices 'Ethernet 1' 'Ethernet 2'
    sudo networksetup -listnetworkserviceorder

iii) Assign static IPs (override DHCP):

  A static IP will be assigned for both Ethernet 1 and Ethernet 2.
  The IP associated with Ethernet 1 will be the one in DNS associated with
  machv2.bioconductor.org. The second IP is necessary to enable bridge
  networking for the VM. The VM will have it's own IP separate from
  the one assigned here, this one is just a placeholder to ensure an
  active network. Depending on how the network is configured, if no static
  IP is assigned to Ethernet 2, this port will consult DNS and get a 
  (potentially) different IP each time. This could cause problems with SSH
  or other means of accessing machv2.

    # RPCI network:
    sudo networksetup -setmanual 'Ethernet 1' 172.29.0.2 255.255.255.0 172.29.0.254 
    sudo networksetup -setmanual 'Ethernet 2' 172.29.0.13 255.255.255.0 172.29.0.254 

Testing:

    sudo ifconfig

To clear settings and go back to DHCP if necessary:

    sudo systemsetup -setdhcp 'Ethernet 1'

iv) Assign the DNS servers:

List DNS servers:

    scutil --dns

Assign DNS servers:

This is only done for Ethernet 1.

    # RPCI network:
    sudo networksetup -setdnsservers 'Ethernet 1' 8.8.8.8 8.8.4.4
    sudo networksetup -setsearchdomains 'Ethernet 1' roswellpark.org

Testing:

    networksetup -getdnsservers 'Ethernet 1'
    ping www.bioconductor.org

v) Apply all software updates and reboot

    softwareupdate -l         # list all software updates
    sudo softwareupdate -ia   # install them all (if appropriate)
    sudo reboot               # reboot

<a name="host-firewall"></a>
### Firewall 

No firewall is enabled on machv2. The information that follows is for
reference if at some future point we decide to enable it.

Mac OSX 10.14.1 Mojave has 2 firewalls: Application Firewall and Packet Filter
(PF).  Both are disabled by default. Should we decide to enable a firewall in
the future, this should probably be done at the system/machine level and not
the application level so it's Packet Filter we are concerned with.

Packet Filter (PF) is OpenBSD's system for filtering TCP/IP traffic and doing
Network Address Translation.

The firewall is disabled by default.

    machv2:~ administrator$ sudo pfctl -s info
    Password:
    No ALTQ support in kernel
    ALTQ related functions disabled
    Status: Disabled

There are three files to be aware of:

  - /etc/pf.conf
  The main configuration file which defines the main rule set.

  - /etc/pf.conf/anchors/com.apple
  The main ruleset loads sub rulesets defined in/etc/pf.anchors/com.apple
  using anchor.

  - /System/Library/LaunchDaemons/com.apple.pfctl.plist
  The launchd configuration file for PF.

NOTE: Firewall rules could be added to com.apple or a new file could be
referenced in pf.conf, however, these files are susceptible to being
overwritten during an OS update. To avoid this, a new file should be created
for each of these three.

NOTE: PF is not only disabled by default but it is silenced at startup. To
enable the service to start when the machine is rebooted you need to disable
System Integrity Protection(SIP). To disable SIP you must boot the machine into
recovery mode which I believe requires a monitor and Apple keyboard. Once
SIP is disabled, modify /System/Library/LaunchDaemons/com.apple.pfctl.plist to
include the '-e' enable flag then re-enable SIP. It is not enough to just
include a plist in /Library/LaunchDaemons that tries to enable the service at
startup because it till conflict with the file in 
/System/Library/LaunchDaemons.

<a name="host-power-management"></a>
### Power management settings

`pmset` manages power management settings such as idle sleep timing, wake on
access, automatic restart on power loss etc.

To see all power management capabilities:

    pmset -g cap

Set `displaysleep`, `disksleep` and `sleep` to zero (FALSE) and `autorestart`
to one (TRUE):

    sudo pmset -a displaysleep 0 disksleep 0 sleep 0 autorestart 1

Confirm the changes by listing the capabilities in use:

    machv2:~ administrator$ pmset -g
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

Remote login will be set to 'off':

    sudo systemsetup -getremotelogin

Set to 'on' and confirm the change:

    sudo systemsetup -setremotelogin on
    sudo systemsetup -getremotelogin
 
<a name="host-remote-events"></a>
### Remote Events and Timezone

Confirm remote events are 'off' (should be off by default):

    sudo systemsetup -getremoteappleevents
    sudo systemsetup -setremoteappleevents off

Confirm timezone is Eastern Standard Time:

    date
    sudo systemsetup -listtimezones
    sudo systemsetup -settimezone America/New_York

<a name="host-parallels"></a>
### Parallels Desktop 

<a name="parallels-install"></a>
#### Install

Parallels Desktop 14 for Mac Business Edition (14.1.0) was used to configure
this VM. The licence was purchased Oct 14, 2018 and is good for one year
(expires Oct 14, 2019).

As the `administrator` user ...

i) Purchase and download Parallels Desktop for Business from the Apple Store.

ii) Register the licence.
    Each licence can be installed on one machine only.

iii) Choose a default location for VM files:

    Go to Preferences -> Virtual machine folder and set this field:
    Virtual machines folder: /Users/administrator/parallels

NOTE: To share VMs across user accounts, the VM files must be in a shared
location with the appropriate permissions. When a VM is shared from
one user to another it must be temporarily suspended before the next user can
access it. This type of sharing isn't applicable to our situation. The
VMs will only be run as the `administrator` user so, for now at least, the
VM files will be in the `administrator` home directory and not a shared
location.

vi) Disable automatic updates

Go to Preferences -> Virtual machine folder and set these fields:

    Check for updates: Never
    Unclick 'Download updates automatically'

Updates should be run manually or scheduled at a known time. Automatic
updates can cause unexpected problems that are difficult to track down.

<a name="parallels-el-capitan-files"></a>
#### Prepare El Capitan files

The El Capitan files are on a UBS key purchased from Amazon.

i) Insert the USB key

ii) View the contents in /Volumes

    machv2:~ administrator$ ls -l /Volumes/
    total 0
    lrwxr-xr-x   1 root           wheel    1 Nov 22 15:37 Macintosh HD -> /
    drwxrwxr-x@ 21 administrator  staff  782 Jan  1  2016 OS X 10.11 Install Disk - 10.11.6

    cd /Volumes/OS X 10.11 Install Disk - 10.11.6

    machv2:~ administrator$ ls -l /Volumes/OS\ X\ 10.11\ Install\ Disk\ -\ 10.11.6/
    total 72
    -rw-r--r--@ 1 administrator  staff  34542 Jul 18 07:14 ElCapitanBackground.png
    drwxr-xr-x  3 administrator  staff    102 Aug 31  2016 Install OS X El Capitan.app
    drwxr-xr-x@ 3 administrator  staff    102 Jul 18 07:14 Library
    drwxr-xr-x@ 3 administrator  staff    102 Jul 18 07:14 System
    drwxr-xr-x+ 9 administrator  staff    306 Jul 18 07:14 Utilities
    -rw-r--r--@ 1 administrator  staff      0 Jul 18 07:14 mach_kernel
    drwxr-xr-x@ 3 administrator  staff    102 Jul 18 07:14 usr

iii) Make a backup of the USB files

    cd /Users/administrator/Parallels
    mkdir el-capitan-usb-backup 

The .app directory is the important one but we'll make a full copy of the USB:

    cd /Volumes
    machv2:Volumes administrator$ ls
    Macintosh HD                      OS X 10.11 Install Disk - 10.11.6
    machv2:Volumes administrator$ cp -r OS\ X\ 10.11\ Install\ Disk\ -\ 10.11.6 /Users/administrator/Parallels/el-capitan-usb-backup/
    cp: OS X 10.11 Install Disk - 10.11.6/.Spotlight-V100: unable to copy extended attributes to /Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/.Spotlight-V100: Operation not permitted
    cp: OS X 10.11 Install Disk - 10.11.6/.Spotlight-V100: Operation not permitted
    cp: OS X 10.11 Install Disk - 10.11.6/.Trashes: unable to copy extended attributes to /Users/administrator/Parallels/el-capitan-usb-backup/OS X 10.11 Install Disk - 10.11.6/.Trashes: Permission denied
    cp: OS X 10.11 Install Disk - 10.11.6/.Trashes: Permission denied

This takes some time. Total size is ~ 6 GB.

    machv2:Parallels administrator$ du -hs /Users/administrator/Parallels/el-capitan-usb-backup/OS\ X\ 10.11\ Install\ Disk\ -\ 10.11.6/*
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

* Click on the Parallels desktop Icon to bring up the Installation Assistant.
  Skip the Windows installation if it prompts for one.

* Click on 'Install Windows or another OS from a DVD or image file'   
  -> Choose manually  
  -> Select a file ...  

* Under 'Locations' choose OSX 10.11 Install Disk  
  -> remove file filters so all files are select-able  
  -> select Install OS X El Capitan

* Parallels will prompt that it needs to make a bootable disk image file.
  Click 'Continue'. Name the image ElCapitan-bootable-image-<date> and
  save the file to /Users/administrator/Parallels.

  Once the bootable image is made you can continue with configuration and
  installation or do it later. The output of this step is the
  /Users/administrator/Parallels/ElCapitan-bootable-image-<date>.hdd file that
  can be used to configure new VMs.

* Remove the USB key

  Using the Finder or the desktop icon, eject the USB and then physically
  remove it from the machine. This step prevents accidental writes to the USB
  key in future steps.

<a name="parallels-configure-and-create"></a>
#### Configure and create the VM

##### Initiate creation 

Click on the Parallels Desktop icon  
  -> Create new VM  
  -> Install Windows or another OS from a DVD or image file  
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

##### Customize settings

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
    suggesting the optimal memory range, allow it to optimize by clicking
    'change' and you'll end up around 57252 MB.  
  Keep all defaults in 'Advanced Settings'

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

Close the configuration window and click 'Continue'. Ignore any prompts 
(i.e., click 'Close') for Parallels to access the camera and microphone. The
machine will boot.

##### Customize installation

A screen will come up prompting the set up the installation of OS X:  
-> click continue  
-> accept terms

A screen will come up asking which disk on which to install OS X:  
-> Choose 'Macintosh HD'

NOTE:  The other option here is 'Install OS X El Capitan'. That is the bootable
disk image (.hdd) we used to create the VM. Do not select this.

Installation takes about 13 minutes

##### Final set up

A series of set-up screens will come up:

  - Choose the country
  - Choose the keyboard configuration
  - Transfer Information to This Mac  
    -> Don't transfer any information now
  - Enable Location Services  
    -> Do not enable this (default is unselected)
  - Don't sign in with your Apple ID
  - Agree to terms and conditions
  - When prompted to create a user account, create `administrator`.  Use the
    same `administrator` password as the other build machines and record this
    in the Google Credentials doc.
  - Select New York EST time zone
  - Diagnostics & Usage  
    -> Deselect 'Send diagnostics & usage data to Apple'  
    -> Deselect 'Share crash data with app developers'

Once set up is complete, detach the boot image file. This image can be used to
launch new VMs so don't put it in the trash (last step).

Detach boot image file:

  - Stop the VM  
    Go to Parallels -> Control Center. Select celaya2 -> Actions -> Stop.  
  - Select the gear icon in celaya2.  
  - Select the Hardware tab -> Hard Disk 2  
  - The .hdd file should be listed in the 'Source' field  
  - Unlock the settings if locked  
  - Disconnect .hdd file by clicking the minus '-'  
  - Select 'Keep files'. Don't move them to the trash.

##### Status check

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

    machv2:~ administrator$ ls -l /Applications/Parallels\ Desktop.app/Contents/Resources/Tools/
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

Start the VM by going to Parallels -> Control Center. Select celaya -> 
Actions -> Start.
  - Click on the yellow triangle with exclaimnation point at the top right 
    of the menu bar.  
  - Follow the prompts to install Parallels Tools.  
  - Installation requires a reboot of the VM. When the prompt comes up, 
    click 'restart'.  
  - If a 'Parallels Tools' icon was left on the VM desktop, click on the icon 
    and eject the disk.  

Alternatively, the tools can be installed on the Guest from a terminal window
on the Host using the `prlctl` command:

    prlctl installtools celaya2


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

Testing:

    scutil --get ComputerName
    scutil --get LocalHostName
    scutil --get HostName
    networksetup -getcomputername

* Restart the VM

<a name="guest-network"></a>
### Network
---------------------------------------------

#### Bridge networking 

Bridge networking allows the VM to access the local network and Internet
through one of the network adapters installed on the Host. The VM Guest will be
treated as an independent computer on the network instead of sharing the same
network connection as the Host.

There are 2 physical ports on the Mac Pro. The first port, Ethernet 1, is used
for the Host and the second port, Ethernet 2, will be used for bridge
networking the Guest VM.  Configuration can be done from the GUI in the running
VM or from a terminal in the Host.

-- Option 1: From the VM Guest

Start the VM if not running.

From within the celaya2 VM, click on the gear icon and the 'hardware' tab. Select 
'Networking'. Under 'Source' select 'Ethernet 2'

Leave the Network Conditioner unselected. Keep all other defaults. 

-- Option 2: From a terminal on the Host

We need to get the name of the physical adapter on the Mac Pro that the VM adapter will be bridged to.

List the network adapters associated with the virtual networks:

    machv2:~ administrator$ networksetup -listnetworkserviceorder
    An asterisk (*) denotes that a network service is disabled.
    (1) Ethernet 1
    (Hardware Port: Ethernet 1, Device: en0)
    
    (2) Ethernet 2
    (Hardware Port: Ethernet 2, Device: en1)
    
    (*) Wi-Fi
    (Hardware Port: Wi-Fi, Device: en2)
    
    (*) Bluetooth PAN
    (Hardware Port: Bluetooth PAN, Device: en9)
    
    (*) Thunderbolt Bridge
    (Hardware Port: Thunderbolt Bridge, Device: bridge0)

A similar (sometimes useful) command with 'Type' included:

    machv2:~ administrator$ prlsrvctl net list
    Network ID        Type      Bound To
    Shared            shared  vnic0 
    NAT server:
    
    Host-Only         host-only  vnic1
    Ethernet 1 (en0)  bridged   en0
    Ethernet 2 (en1)  bridged   en1
    en5 (en5)         bridged   en5
    en6 (en6)         bridged   en6
    en3 (en3)         bridged   en3
    en4 (en4)         bridged   en4
    en7 (en7)         bridged   en7
    en8 (en8)         bridged   en8
    vnic0 (vnic0)     bridged   vnic0
    vnic1 (vnic1)     bridged   vnic1
    Default           bridged   FF:FF:FF:FF:FF:FF

The Host is using Ethernet 1 (en0) and the Guest will use Ethernet 2 (en1).
The output above shows the 'Ethernet 2 (en1)' virtual network is attached to
the 'en1' physical adapter.

To connect the VM to the 'Ethernet 2 (en1)' network we need to know the name of
the network adapter on the VM.  Use `prlctl list` to see the networking on the
VM. 

This output was truncated but the important thing to note is the networking on
'net0' adapter of the VM. By default it will say 'shared': 

    machv2:Library administrator$ prlctl list celaya2 -i
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

    machv2:Library administrator$ prlctl set celaya2 --device-set net0 --type bridged --iface en1
    Configure net0 (+) type=bridged iface='Ethernet 2' mac=001C42B43DED card=e1000
 
    Configured net0 (+) type=bridged iface='Ethernet 2' mac=001C42B43DED card=e1000
 
 
    The VM has been successfully configured.

Confirm net0 is bridged to en1:

    machv2:Library administrator$ prlctl list celaya2 -i
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

#### Assign static IP:

The IP, subnet and router information came from RPCI. 

Query VM for network adapter name:

    celaya2:~ administrator$ networksetup -listnetworkserviceorder
    An asterisk (*) denotes that a network service is disabled.
    (1) Ethernet
    (Hardware Port: Ethernet, Device: en0)

Set the static IP, subnet mask and router:

    # RPCI network:
    sudo networksetup -setmanual 'Ethernet' 172.29.0.12 255.255.255.0 172.29.0.254 

Testing:

    sudo ifconfig

#### Assign DNS servers:

List DNS servers:

    scutil --dns

Assign DNS servers:

    # RPCI network:
    sudo networksetup -setdnsservers 'Ethernet' 8.8.8.8 8.8.4.4
    sudo networksetup -setsearchdomains 'Ethernet' roswellpark.org

Testing:

    networksetup -getdnsservers 'Ethernet'
    ping celaya2.bioconductor.org

Apply all software updates and reboot

    softwareupdate -l         # list all software updates
    sudo softwareupdate -ia   # install them all (if appropriate)
    sudo reboot               # reboot

#### Allow worker to talk to master Linux builder

As of January 2019, we still had build machines in MacStadium that needed to 
talk to the master Linux builders on a public IP. Because of this, the
DNS entries for the master Linux builders resolve to the public IP. This
worker, celaya2, is going to live in the RPCI DMZ and needs to talk
to the master builder on the RPCI private IP. This is accomplished by
adding this line to /etc/hosts:

    172.29.0.4   malbec2.bioconductor.org malbec2 

Once we no longer have machines in MacStadium, the Route53 DNS entry for
the master Linux builders can be modified to point to the private IP and
we can remove the line above from the hosts file.

<a name="guest-firewall"></a>
### Firewall 

No firewall is enabled on `celaya2`. See the section on Firewalls for the
Host for additional details.

<a name="guest-power-management"></a>
## Power Management settings

This command is run from the terminal on the Host (no sudo needed). It
instructs Parallels to start the VM when the host starts up, i.e., on reboot,
prevents pause when idle or when windows close. 

    prlctl set celaya2 --autostart start-host --pause-idle off --on-window-close keep-running

We also need to run a command from within the VM that prevents the Guest from
sleeping and enables auto-restart.  Open a terminal window inside the VM and
run

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

<a name="guest-remote-events"></a>
## Remote Events and Timezone

Confirm remote events are 'off' (should be off by default):

    sudo systemsetup -getremoteappleevents
    sudo systemsetup -setremoteappleevents off

Confirm timezone is Eastern Standard Time:

    date
    sudo systemsetup -listtimezones
    sudo systemsetup -settimezone America/New_York


<a name="guest-disable-sip"></a>
## Disable System Integrity Protection (SIP)

One of the system requirements for configuring the VM as a builder is
to install libsbml. This used to be available via brew and it was installed
in /usr/local/Cellar. They have since dropped it. For this installation,
it was downloaded from SourceForge and was installed in /usr/local/lib and 
/usr/local/bin. 

Everything I've read indicates that /usr/local should not a SIP protected area, 
however, that was not my experience. The runtime linker could not find
the /usr/local/lib/libsbml.5.dynlib.

I tried adding the path to /etc/profile DYLD_LIBRARY_PATH but these variables
were ignored when launching protected processes.

There may be another way around this but for the time being I've disabled
SIP on celaya2 so the path could be added to /etc/profile DYLD_LIBRARY_PATH.

To disable SIP you must boot into recovery mode. A monitor, keyboard and 
mouse are necessary. Follow instructions here:

https://kb.parallels.com/en/116526

Once in recovery mode:

    csrutil disable
    reboot

The machine should reboot into "regular" mode with SIP disabled:

    csrutil status

<a name="configure-vm-guest-as-build-machine"></a>
## Configure VM Guest as build machine
------------------------------------------------------------------------------

Follow instructions in 
[Prepare-Mac-OSX-El-Capitan-HOWTO.TXT](https://github.com/Bioconductor/BBS/blob/master/Doc/Prepare-MacOSX-El-Capitan-HOWTO.TXT) to configure the VM Guest
as a build machine.

Start with Section B since the user accounts have already been set up.
