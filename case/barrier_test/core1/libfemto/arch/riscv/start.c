// See LICENSE for license details.

#include "femto.h"
#include "arch/riscv/encoding.h"
#include "arch/riscv/machine.h"

extern char _bss_start;
extern char _bss_end;
extern char _memory_end;

int main(int argc, char **argv);
int hipu_main(int argc, char **argv);

__attribute__((noreturn)) void libfemto_start_main()
{
	char *argv[] = { "femto", NULL };
	int hart_id;
	asm volatile("csrr %0, mhartid":"+r"(hart_id)::);

	memset(&_bss_start, 0, &_bss_end - &_bss_start);
	arch_setup();
	_malloc_addblock(&_bss_end, &_memory_end - &_bss_end);

	exit(main(1, argv));
	__builtin_unreachable();
}

__attribute__((noreturn)) void libfemto_start_main_hipu()
{
	char *argv[] = { "femto", NULL };
	memset(&_bss_start, 0, &_bss_end - &_bss_start);
	arch_setup();
	_malloc_addblock(&_bss_end, &_memory_end - &_bss_end);
	printf("(Huang)libfemto_start_mai_hipun\n\r");

	exit(main(1, argv));
	__builtin_unreachable();
}