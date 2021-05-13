#include <stdio.h>

int main(int argc, char **argv)
{
	printf("hello\n");
	asm(".word 0xdeadbeef":::);
}
