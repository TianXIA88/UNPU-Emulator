# bootloader

## How to use
To run multicore, enter the command:
>$YOUR_QEMU_PATH/bin/qemu-system-riscv32 -nographic -machine sifive_u -smp 2 -m 2G -device loader,file=$YOUR_FISRT_ELF_FOR_CORE0,addr=0x8fffff00,force-raw=on  -device loader,addr=0x90000000,cpu-num=0  -device loader,file=$YOUR_SECOND_ELF_FOR_CORE1,addr=0x9fffff00,force-raw=on  -device loader,addr=0xa0000000,cpu-num=1

In this command, the addr loaded into the file is **0x100** smaller than the PC run by the real CPU. This is caused by the header file information of elf.

NOTE that QEMU init happens in **0x80000000**. If there are more threads specified in argument '-smp' than specific elf you want to run, you should create an elf and load it to 0x80000000 so other threads can park.

## Environment
QEMU5.0

## Verification of multi-core functions

### Independent startup of different CPUs
The command `-device loader,addr=0x90000000,cpu-num=0` makes **hart0** begins at **0x90000000**. By this way, we can make different Hart execute at different starting addresses.

### NUMA communication
NUMA communication contains two ways:

**1. Access shared variable.**

We set a shared variable **flag** in the shared address space to keep the order. (NOTE that the premise of flag's modification is to get the **lock**)

When we want to modify input data, we should first set flag as 0, which means the content is being writed. 
Similarly, when we complete the modification, we should flag as 1, which means the content is free, so you can perform your other operations.

**2. NDMA.**

We use NMDA to communicate with different Hart's local memory. 
Note that arguments `rm_x` and `rm_y` determine the remote hart we want to communicate here.
In this example, the data flow can be described as followings:

**DDR -> Hart0 -> Hart1**

### Lock
To modify flag, we should first get the lock.
The lock is placed on the lock_addr. We use atomic instructions `amoswap.w.aq` and `amoswap.w.rl` to achieve the acquisition and release of lock.