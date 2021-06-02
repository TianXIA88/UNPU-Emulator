#include <stdio.h>

int main(int argc, char **argv)
{
	asm(".word 0xdeadbeef":::);
    // asm(".word 0x101090ab":::); // undefined instruction
	printf("hello\n");
    while(1);;
}
