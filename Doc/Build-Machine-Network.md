# Build Machine Network

As of January 2019, we have build machines in both the RPCI DMZ and MacStadium:

RPCI DMZ:

malbec1 (Linux master)
malbec2 (Linux master)
tokay1  (Windows worker)
tokay2  (Windows worker)
celaya2 (Mac worker)

MacStadium:

merida1 (Mac worker)
merida2 (Mac worker)

The goal is to host both Mac builders inside the RPCI DMZ and close out
our account with MacStadium. We currently have one new Mac builder in
the DMZ, celaya2, and 2 builders in MacStadium.

## IPs

All machine IPs are listed in the Google Credentials Doc.

## Network communication

Communication direction within the build system is from worker to master. The
master does not initiate communication with the workers. When machines within
the DMZ communicate they do so on the private IPs. When the MacStadium machines
initiate contact with a master Linux builder they do so on a public IP because
they do not have RPCI private IPs (they probably have private IPs for the
MacStadium network but that is not important here).

The only machines that need public IPs are the master builders because they are
accessed by the MacStadium workers that are outside the DMZ.  The workers
inside the DMZ communicate with the master builders on the private IP.  Because
DNS resolves to the public IP, the workers inside the DMZ must override this by
including an entry in their hosts file that points to the private IP.  This
override could potentially be done in the BBS code but the disadvantage is that
we would have to hard code IPs instead of using the hostname.  Once the
MacStadium machines are gone, we no longer need the public IPs for the master
builders and the hosts files on the workers can be cleaned up.

## Route53 DNS

Currently the DNS entries in Route53 resolve to the private IPs for the
workers inside the DMZ and public IPs for masters.

Once we no longer have MacStadium machines, the master builders can also
resolve to their private IPs since nothing from outside the DMZ should 
need to access them. When that happens, make these DNS changes in Route53:

Name: malbec1.bioconductor.org
Type: A
Value: 172.29.0.3 

Name: malbec2.bioconductor.org
Type: A
Value: 172.29.0.4

## hosts file on workers

And the hosts files on the Windows and Mac builders can be cleaned up
by removing the entry that points to the private IP.

On the '1' series workers, remove this line from the hosts file:

    172.29.0.3   malbec1.bioconductor.org malbec1

On the '2' series workers, remove this line from the hosts file:

    172.29.0.4   malbec2.bioconductor.org malbec2

The file is located at /etc/hosts on the Mac 
and C:\Windows\System32\Drivers\etc\hosts on Windows.
