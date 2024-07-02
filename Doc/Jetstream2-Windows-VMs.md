# Jetstream2 Windows VMs 


This guide provides a broad outline for creating a Windows VM in Jetstream2,
retrieving the password to log into the Administrator account through the
console, adding a rule to the security group to allow RDP access, and accessing
the machine through RDP.


## Create the VM on Jetstream2

Use https://js2.jetstream-cloud.org/ rather than Exosphere to set up the VM
as creating a VM in Exosphere may get stuck "building".

Note: Windows VMs in Jetstream2 are experimental and will need a license. See the
[Microsoft Windows on Jetstream2](https://docs.jetstream-cloud.org/general/windows/)
for more details.


Click on `Launch instance` and fill in the details as below:

- Details
  - Instance Name: `palomino`

- Source
  - Select Boot Source: image
  - Create New Volume: Yes
  - Volume Size: 1024 Gb
  - Delete Volume on Instance Delete: Yes
  - Allocated: Windows-Server-2022-JS2-Beta

- Flavor: m3.2xl (64 VCPUS 250 GB RAM)

- Security Groups: BBS Windows

- Key Pair:
  Use `BBS palomino` or `Create Key Pair`, where Key Type is `SSH Key`. Without
  this, you won't be able to log into the machine. When you create the key
  pair, your browser will automatically download the pem file that you use to
  decrypt the Administrator password.

Click `Launch Instance` to build the VM.


## Retrieve Administrator Password

After your VM is built, you can retrieve the password to log in through the
console.

From `Compute > Instances`, locate your VM. From the righthand menu in the
row of your instance, select `Retrieve Password`.

Upload or paste your private key from the key pair specified in VM creation.

Click `Decrypt Password` and copy the `Password`.


## Log into Administrator Account

From the righthand menu in the row of your instance, select `Console`.

Click on `Send Ctrl-Alt-Delete` to get the prompt for the Administrator
password.

Enter the decrypted password.


## Associate a Floating IP

The floating IP will be the public IP for the machine. From
`Compute > Instances`, select Associate Floating IP.

If an IP isn't available, click on the `+` button to acquire one.


## Add a Rule to the Network Security Group to Allow RDP

To access the VM through RDP, you must add a rule to allow your IP RPD access.

From `Network > Security Groups`, click on `Manage Rules` for your VM.

Click `Add Rule`.

- Rule: RDP
- Remote: CIDR
- CIDR: Your IP

Click Add.


## Access VM through RDP

Once your VM has been configured to allow RPD, you can access it through a
program like Remmina.

In the connection profile, set the following

- Protocol: RDP
- Server: (the Floating IP you assigned in the previous step followed by
  `:3389`)
- Username: (the user you created in the VM)
- Password: *****
