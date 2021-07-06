#include <stdio.h>
#include "arch/riscv/encoding.h"
#include "arch/riscv/machine.h"
#include "arch/riscv/csr.h"

int main(int argc, char **argv)
{
	int *tmp = 0x2000000;
    int value;
    // value = read_csr_enum(csr_mcause);
    // printf("mcause = %x\n", value);
    // asm(".word 0xdeadbeef":::);
    // asm(".word 0x101090ab":::); // undefined instruction
    // printf("---------------\n\r");
    write_csr_enum(csr_mstatus, MSTATUS_MIE);
    // value = read_csr_enum(csr_mstatus);
    // printf("mstatus = %x\n", value);
    // value = read_csr_enum(csr_mie);
    // printf("mie = %x\n", value);
    // value = read_csr_enum(csr_mip);
    // printf("mip = %x\n", value);
    write_csr_enum(csr_mie, MSTATUS_MIE);
    // value = read_csr_enum(csr_mie);
    // printf("mie = %x\n", value);
    // value = read_csr_enum(csr_mcause);
    // printf("mcause = %x\n", value);

    tmp[0] = 1;
	
    // value = read_csr_enum(csr_mip);
    // printf("mip = %x\n", value);
    // value = read_csr_enum(csr_mcause);
    // printf("mcause = %x\n", value);

    printf("hello\n");
    asm(".word 0xdeadbeef":::);
    asm(".word 0xdeadbeef":::);
    while(1);;
}
