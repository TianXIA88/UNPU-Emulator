.section .text
.global main
main:
	.word 0x1eadbeef 	# dma to init MMA MMB
	li t0, 0x2002		# t0 = 0x2002
	.word 0xcff2802b	# "vlb", imm=-1, sr=5, vr=0
	li t0, 0x2		# t0 = 0x2
	.word 0x001280ab	# "vlb", imm= 1, sr=5, vr=1
	.word 0x0000912b	# "vadd", mode="vv", dst=2, op1=0, op2=1, vpr=0
	li t1, -1		# t1 = -1
 	.word 0x012311ab	# "vadd", mode="vs", dst=3, op1=2, op2=6, vpr=0	
	.word 0x10312a2b	# "vsrl", mode="vi", dst=4, op1=3, op2=2, vpr=0
	li t1, 2
	.word 0x01432a2b	# "vsll", mode="vs", dst=4, op1=4, op2=6, vpr=0
	li t1, 0x53977		# t1 = (0,1,2,3,4,5,6,7)
	.word 0x0143322b	# "valh",            dst=4, op1=4, op2=6
	.word 0x1143322b	# "valv",            dst=4, op1=4, op2=6
	.word 0x3040402b	# "vpge", mode="vv", dst=0, op1=4, op2=0
	.word 0x300048ab	# "vpnot",           dst=1, op1=0
	.word 0x0000d02b	# "vpswap",                 op1=0, op2=1
	li t0, 0x0
	li t1, 0x2000
	.word 0x0642928b	# "mdmad",     	     dst=5, op1=5, op2=6, op3=4
	.word 0x2642d30b	# "mdmad",mode="ad", dst=6, op1=5, op2=6, op3=4
	.word 0x0642d38b	# "mdmad",mode="au", dst=7, op1=5, op2=6, op3=4
	.word 0x0642840b	# "mmad",            dst=8, op1=5, op2=6, op3=4
	.word 0x0642a48b	# "mvmad",           dst=9, op1=5, op2=6, op3=4
	li t2, 0x10             # t2 = 0x10
	.word 0x20038aab 	# "vsw", imm=0, sr=7, vr=5

 	la t0, _main
 	jr t0
