About VM sizes:

  https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-compute

Nb of logical cpus and prices of various VM sizes (in USD/month) as of Dec 2021:

    VM size      nb logical cpus      price
    ---------    ---------------    -------
    DS1_v2                     1      91.98

    D32s_v5                   32    2195.84
    D48ads_v5                 48         NA
    D48as_v5                  48         NA
    D48ds_v5                  48    3591.60
    D48s_v5                   48    3293.76
    D48s_v4                   48    3293.76
    D48_v5                    48    3293.76
    D48d_v5                   48    3591.60

    B20ms                     20     665.76

    F16s_v2                   16     950.46
    F32s_v2                   32    1900.92
    F48s_v2                   48    3095.20

Notes:

- Both DS1\_v2 and B20ms sizes run on the
  Intel(R) Xeon(R) CPU E5-2673 v4 processor cadenced at 2.30 GHz.
  This processor has 20 cores and support 40 threads (i.e. 40 logical
  cpus). Nice but:
  - the DS1\_v2 VM only makes 1 logical core available
    and the B20ms only 20
  - these logical cpus are weak when taken individually

- According to the official document on VM sizes above:

  > The Fsv2-series runs on 2nd Generation Intel® Xeon® Platinum 8272CL
  > (Cascade Lake) processors and Intel® Xeon® Platinum 8168 (Skylake)
  > processors. It features a sustained all core Turbo clock speed of
  > 3.4 GHz and a maximum single-core turbo frequency of 3.7 GHz. 

  However, setting up a VM of size F16s\_v2 reveals an Intel(R) Xeon(R)
  Platinum 8272CL CPU processor cadenced at 2.6 GHz only (according to
  the Task Manager), which is kind of disappointing.

- For reference, our Windows builder riesling1 (DeLL machine running
  Windows Server 2019) has 2 Intel(R) Xeon(R) Gold 6242R CPU processors
  cadenced at 3.10 GHz.
  Some quick benchmarking:
  ```
                     palomino     palomino2    riesling1
                      (B20ms)    (F16s\_v2)
                    ----------   ----------   ----------
  INSTALL
  BiocGenerics:         79.5 s         ??         43.6 s
  IRanges:             220.5 s      172.1 s      101.8 s
  mzR:                 937.1 s      854.1 s      520.9 s
  ```


## palomino

### Basics

  - Subscription: MS Genomics RnD-PoC
  - Resource group: bioconductor
  - Virtual machine name: palomino
  - Region: East US
  - Availability options: No infrastructure redundancy required
  - Security type: Standard
  - Image: Windows Server 2022 Datacenter: Azure Edition - Gen2
  - Azure Spot instance: no
  - Size: Standard B20ms (20 vcpus, 80 GiB memory)
  - Username: palomino
  - Public inbound ports: Allow selected ports
  - Select inbound ports: RDP (3389)
  - Would you like to use an existing Windows Server license?: no

### Disks

  - OS disk type: Premium SSD (locally-redundant storage)
  - Delete with VM: yes
  - Encryption type: default
  - Create and attach a new disk:
    - Name: keep default (palomino\_DataDisk\_0)
    - Source type: None (empty disk)
    - Size: size 1024 GiB
    - Encryption type: default
    - Enable shared disk: no
    - Delete disk with VM: yes

### Networking

  - Virtual network: vNet
  - Subnet: keep default (subnet (10.0.0.0/24))
  - Public IP: (new) palomino-ip
  - NIC network security group: Basic
  - Public inbound ports: Allow selected ports
  - Select inbound ports: RDP (3389)
  - Delete public IP and NIC when VM is deleted: yes
  - Accelerated netwrorking: yes
  - Place this virtual machine behind an existing load balancing solution: no

IP: 20.120.103.38 (Static)

### Management & Advanced & Tags
  - keep all defaults


## palomino2

Same as palomino except for the size: 
  - Size: F16s\_v2

IP: 20.121.0.218 (Static)


## tinybuilder

### Basics

  - Subscription: MS Genomics RnD-PoC
  - Resource group: bioconductor
  - Virtual machine name: tinybuilder
  - Region: East US
  - Availability options: No infrastructure redundancy required
  - Security type: Standard
  - Image: Windows Server 2022 Datacenter: Azure Edition - Gen2
  - Azure Spot instance: no
  - Size: Standard DS1\_v2 (1 vcpu, 3.5 GiB memory)
  - Username: tinybuilder
  - Public inbound ports: Allow selected ports
  - Select inbound ports: RDP (3389)
  - Would you like to use an existing Windows Server license?: no

### Disks

  - OS disk type: Premium SSD (locally-redundant storage)
  - Encryption type: default

### Networking

  - Virtual network: vNet
  - Subnet: keep default (subnet (10.0.0.0/24))
  - Public IP: (new) tinybuilder-ip
  - NIC network security group: Basic
  - Public inbound ports: Allow selected ports
  - Select inbound ports: RDP (3389)
  - Accelerated netwrorking: yes
  - Place this virtual machine behind an existing load balancing solution: no

IP: 13.68.155.251 (Static)

### Management & Advanced & Tags
  - keep all defaults

