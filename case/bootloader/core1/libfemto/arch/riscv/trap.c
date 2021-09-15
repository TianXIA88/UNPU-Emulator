// See LICENSE for license details.

#include "femto.h"
#include "arch/riscv/trap.h"
#include "arch/riscv/encoding.h"
#include "arch/riscv/machine.h"
#include "arch/riscv/csr.h"

static trap_fn tfn = 0;

#define csrw(a, s)      asm("csrw  %0, %1 "::"i"(a),"r"(s):)
#define CSR_ADDR_NDMA_CTRL                      (0x7C0)
#define ndma_start(x)           csrw(CSR_ADDR_NDMA_CTRL, x)

// const char * riscv_excp_names[16] = {
//     "misaligned_fetch",
//     "fault_fetch",
//     "illegal_instruction",
//     "breakpoint",
//     "misaligned_load",
//     "fault_load",
//     "misaligned_store",
//     "fault_store",
//     "user_ecall",
//     "supervisor_ecall",
//     "hypervisor_ecall",
//     "machine_ecall",
//     "exec_page_fault",
//     "load_page_fault",
//     "reserved",
//     "store_page_fault"
// };

// const char * riscv_intr_names[16] = {
//     "u_software",
//     "s_software",
//     "h_software",
//     "m_software",
//     "u_timer",
//     "s_timer",
//     "h_timer",
//     "m_timer",
//     "u_external",
//     "s_external",
//     "h_external",
//     "m_external",
//     "reserved",
//     "reserved",
//     "reserved",
//     "reserved"
// };

trap_fn get_trap_fn()
{
    return tfn;
}

void set_trap_fn(trap_fn fn)
{
    tfn = fn;
}

void trap_handler(uintptr_t* regs, uintptr_t mcause, uintptr_t mepc)
{
    int msip_hart_base = 0x2000000;
	int hart_id, msip_hart_addr;
    printf("mcause: trap %d @ %p\n\r", mcause, mepc);
    printf("trap handler!\n\r");
   
    asm volatile("li a0, 0");
	// for(int i = 1; i<5; i++){
	// 	msip_hart_addr = msip_hart_base + 4 * i;
	// 	asm volatile("sw a0, (%0)":"+r"(msip_hart_addr)::);
	// }
    if (tfn) {
        tfn(regs, mcause, mepc);
    } else {
        die("machine mode: unhandlable trap %d @ %p", mcause, mepc);
    }
}

void machine_soft_handler(uintptr_t* regs, uintptr_t mcause, uintptr_t mepc)
{
    int msip_hart_base = 0x2000000;
	int hart_id, msip_hart_addr;
    printf("mcause: trap %x @ %p\n\r", mcause, mepc);
    printf("machine soft handler!\n\r");
   
    
	asm volatile("csrr %0, mhartid":"+r"(hart_id)::);

    asm volatile("li a0, 0");
    msip_hart_addr = msip_hart_base + 4 * hart_id;
	asm volatile("sw a0, (%0)":"+r"(msip_hart_addr)::);
	
    // printf("tfn = %d\n\r", tfn);
    // if (tfn) {
    //     tfn(regs, mcause, mepc);
    // } else {
    //     die("machine mode: unhandlable trap %d @ %p", mcause, mepc);
    // }
}


void ndma_handler(uintptr_t* regs, uintptr_t mcause, uintptr_t mepc)
{
    int ndma_hart_base = 0x2006000;
    int hart_id, ndma_hart_addr;
    printf("mcause: trap %x, mepc: %x mip: %x\n\r", mcause, mepc, read_csr_enum(csr_mip));
    printf("ndma interrupt\n\r");
    ndma_start(0xff000003);
    // printf("tfn = %d\n\r", tfn);
    return;
    
	// asm volatile("csrr %0, mhartid":"+r"(hart_id)::);
    // ndma_start(0xff000003);
    // asm volatile("li a0, 0");
    // ndma_hart_addr = ndma_hart_base + 4 * hart_id;
	// asm volatile("sw a0, (%0)":"+r"(ndma_hart_addr)::);
	
    // if (tfn) {
    //     tfn(regs, mcause, mepc);
    // } else {
    //     die("machine mode: unhandlable trap %d @ %p", mcause, mepc);
    // }
}

void timer_handler(uintptr_t* regs, uintptr_t mcause, uintptr_t mepc)
{
    printf("mcause: trap %d\n\r", mcause);
    printf("timer interrupt!\n\r");
    // if (tfn) {
    //     tfn(regs, mcause, mepc);
    // } else {
    //     die("machine mode: unhandlable trap %d @ %p", mcause, mepc);
    // }
}
