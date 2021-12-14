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
  cpus). Nice, but:
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
  Windows Server 2019) has two Intel(R) Xeon(R) Gold 6242R CPU processors
  cadenced at 3.10 GHz. Each processor has 40 logical cores.
  Some timings (in seconds), using R 4.2 + Rtools40:
  ```
                                 INSTALL     BUILD      CHECK    BUILD BIN
  BiocGenerics 0.41.2 --------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       43.6        1.3       54.2       43.4
    o palomino (B20ms) . . . .       37.9        5.1     (634.3)
    o palomino2 (F16s_v2)  . .       34.7        4.3       69.6       80.6
  Biostrings 2.63.0 ----------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       79.3      123.6      459.3       88.8
    o palomino (B20ms) . . . .      165.2      200.1   (TIMEOUT)
    o palomino2 (F16s_v2)  . .      135.6      232.3      597.9      116.2
  csaw 1.29.1 ----------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .      123.2       87.9      387.1       74.6
    o palomino (B20ms) . . . .      143.3      149.7
    o palomino2 (F16s_v2)  . .      143.0      121.8      545.5      139.8
  DelayedMatrixStats 1.17.0 --  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       83.0      210.0      221.6       50.2
    o palomino (B20ms) . . . .       62.5      313.4
    o palomino2 (F16s_v2)  . .       47.9      281.7      299.2       37.6
  DESeq2 1.35.0 --------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       92.2      157.3      386.9       77.3
    o palomino (B20ms) . . . .       95.7      205.0
    o palomino2 (F16s_v2)  . .       91.2      176.5      508.6       88.6
  flowCore 2.7.0 -------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .      119.9      151.5      144.3      123.0
    o palomino (B20ms) . . . .      202.9      239.7
    o palomino2 (F16s_v2)  . .      187.0      239.8      199.1      153.0
  IRanges 2.29.1 -------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       99.7       93.1      169.7       97.4
    o palomino (B20ms) . . . .      184.9      145.7
    o palomino2 (F16s_v2)  . .      166.0      143.1      235.7      131.2
  minfi 1.41.1 ---------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       75.4      102.4      414.6       53.8
    o palomino (B20ms) . . . .       90.5      406.2
    o palomino2 (F16s_v2)  . .       68.1      202.9      532.1
  mzR 2.29.1 -----------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .      477.8      659.2      ERROR      541.9
    o palomino (B20ms) . . . .      888.5     3586.6
    o palomino2 (F16s_v2)  . .      750.9      811.4      179.2
  RBGL 1.71.0 ----------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       93.0       83.0       48.4       87.0
    o palomino (B20ms) . . . .      141.8      678.4
    o palomino2 (F16s_v2)  . .      116.0      136.1       69.7
  VariantAnnotation 1.41.3 ---  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       92.2      157.3      386.9       77.3
    o palomino (B20ms) . . . .      154.8
    o palomino2 (F16s_v2)  . .      145.1      281.2      709.6
  zlibbioc 1.41.0 ------------  ---------  ---------  ---------  ---------
    o riesling1  . . . . . . .       49.6       12.1       25.9       24.3
    o palomino (B20ms) . . . .       25.0      (23.2)
    o palomino2 (F16s_v2)  . .       20.7       19.1       31.3
  ```
  TIMEOUT limit is 80 min.
  BBS\_BUILD\_NB\_CPU=9 and BBS\_CHECK\_NB\_CPU=10 on palomino (20 logical
  processors).
  BBS\_BUILD\_NB\_CPU=12 and BBS\_CHECK\_NB\_CPU=13 on palomino2 (16 logical
  processors).

  Why not use more cpus on palomino? On an earlier attempt with palomino,
  we had BBS\_CHECK\_NB\_CPU set to 16. However when the builds entered the
  CHECK stage on this machine, the Task Manager started to show a steady CPU
  utilization of 100% and `R CMD check` was timing out on half of the packages.
  At this point the VM was only able to process about 14 packages per hour!
  We stopped the VM after it had been in the CHECK stage for about 21 hours
  and only able to run `R CMD check` on 300 packages so far.


## palomino

### Basics

  - Subscription: ******************
  - Resource group: ************
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

### Management & Advanced & Tags
  - keep all defaults


## palomino2

Same as palomino except for the size:
  - Size: F16s\_v2


## tinybuilder

### Basics

  - Subscription: ******************
  - Resource group: ************
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

### Management & Advanced & Tags
  - keep all defaults

