#include <stdio.h>
#include "arch/riscv/encoding.h"
#include "arch/riscv/machine.h"
#include "arch/riscv/csr.h"

int main(int argc, char **argv)
{
	// int *tmp = 0x2000000;
    int value;
    // value = read_csr_enum(csr_mcause);
    // printf("mcause = %x\n", value);
    // asm(".word 0xdeadbeef":::);
    // asm(".word 0x101090ab":::); // undefined instruction
    printf("---------------\n\r");
    // write_csr_enum(csr_mstatus, MSTATUS_MIE);
    // value = read_csr_enum(csr_mstatus);
    // printf("mstatus = %x\n", value);
    // value = read_csr_enum(csr_mie);
    // printf("mie = %x\n", value);
    // value = read_csr_enum(csr_mip);
    // printf("mip = %x\n", value);
    // write_csr_enum(csr_mie, MSTATUS_MIE);
    // value = read_csr_enum(csr_mie);
    // printf("mie = %x\n", value);
    // value = read_csr_enum(csr_mcause);
    // printf("mcause = %x\n", value);

    // tmp[0] = 1;
	
    // value = read_csr_enum(csr_mip);
    // printf("mip = %x\n", value);
    // value = read_csr_enum(csr_mcause);
    // printf("mcause = %x\n", value);

    write_csr(0x730, 3);        // CSR_VLD_LOOP0_NUM 
    write_csr(0x731, 1);        // CSR_VLD_LOOP0_STEP
    write_csr(0x732, 2);        // CSR_VLD_LOOP1_NUM 
    write_csr(0x733, 10);       // CSR_VLD_LOOP1_STEP
    write_csr(0x734, 2);        // CSR_VLD_LOOP2_NUM 
    write_csr(0x735, 100);      // CSR_VLD_LOOP2_STEP
    write_csr(0x736, 8);        // CSR_VST_LOOP0_NUM 
    write_csr(0x737, 100);      // CSR_VST_LOOP0_STEP
    write_csr(0x738, 1);        // CSR_VST_LOOP1_NUM 
    write_csr(0x739, 1000);     // CSR_VST_LOOP1_STEP
    write_csr(0x73a, 1);        // CSR_VST_LOOP2_NUM 
    write_csr(0x73b, 10000);    // CSR_VST_LOOP2_STEP
    asm(".word 0x1eadbeef":::); // vloop start
    asm(".word 0x3eadbeef":::); // vld at addr=100
    asm(".word 0x4eadbeef":::); // vst at addr=1000
    asm(".word 0x2eadbeef":::); // vloop end
    printf("hello\n");
    // asm(".word 0xdeadbeef":::);
    while(1);;
}
