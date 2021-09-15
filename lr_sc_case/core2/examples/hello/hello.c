#include <stdio.h>
#include <arch/riscv/spinlock.h>

#define DMA_TX_CMD                  (0)
#define DMA_RX_CMD                  (1)

#define QEMU_LOG_MEM     0
#define QEMU_LOG_MMAB    1

#define CSR_ADDR_NDMA_CTRL                      (0x7C0)
#define CSR_ADDR_NDMA_STATUS                    (0x7C1)
#define CSR_ADDR_NDMA_LCADDR                    (0x7C2)
#define CSR_ADDR_NDMA_RTADDR                    (0x7C3)
#define CSR_ADDR_NDMA_SIZE                      (0x7C4)
#define CSR_ADDR_NDMA_DESTXY                    (0x7C5)
#define CSR_ADDR_VMU_STATUS                     (0x7Cf)
#define DMA_STATUS_MASK             (0xff000000)
#define CSR_FPRINT_ADDR                         (0xBE2)
#define CSR_FPRINT_LEN                          (0xBE3)

#define _set_bit_intr_mie(x)           asm("csrs mie,       %0"::"r"(x):)
#define _set_bit_intr_mstatus(x)       asm("csrs mstatus,   %0"::"r"(x):)

#define ndma_xy(x, y)           (((x)&0x3)<<2)+((y)&0x3)

#define ndma_cfg(xy, r, l, s)   csrw(CSR_ADDR_NDMA_RTADDR, (r));    \
                                csrw(CSR_ADDR_NDMA_DESTXY, (xy));   \
                                csrw(CSR_ADDR_NDMA_LCADDR, (l));    \
                                csrw(CSR_ADDR_NDMA_SIZE, (s));  

#define ndma_start(x)           csrw(CSR_ADDR_NDMA_CTRL, x)


#define vmu_poll()              {   int poll = 0;                      \
                                    do{                                     \
                                        csrr(poll, CSR_ADDR_VMU_STATUS);    \
                                    }while((poll) != (0x7));                \
                                }


#define csrw(a, s)      asm("csrw  %0, %1 "::"i"(a),"r"(s):)
#define csrr(s, a)      asm("csrr  %0, %1":"+r"(s):"i"(a):)

#define ndma_over_poll(x)       do{                                     \
                                    csrr(x, CSR_ADDR_NDMA_STATUS);      \
                                }while(((x) & DMA_STATUS_MASK) == 0);   \
                                x = 0xffffffff;                         \
                                csrw(CSR_ADDR_NDMA_CTRL, x)

void __ndma_poll(){
    int poll = 0;
    ndma_over_poll(poll);
}

int __rd_from_remote_chunk_non_blocking(int *var, int rm_x, int rm_y, int rm_addr, int size){
    if(size & 0x3f) // must align with 64 Byte
        return -1;
    else{

        // vmu_poll();
        ndma_cfg(ndma_xy(rm_x, rm_y), rm_addr, var, size);
        ndma_start(DMA_RX_CMD);
        return 0;
    }
}

int __rd_from_remote_chunk_blocking(int *var, int rm_x, int rm_y, int rm_addr, int size){

    if(__rd_from_remote_chunk_non_blocking(var, rm_x, rm_y, rm_addr, size))
        return -1;
    __ndma_poll();
	
    return 0;
}

int __wr_rm_chunk_non_blocking(int *var, int rm_x, int rm_y, int rm_addr, int size){
    if(size & 0x3f)
        return -1;
    else{
        ndma_cfg(ndma_xy(rm_x, rm_y), rm_addr, var, size);
        ndma_start(DMA_TX_CMD);
        return 0;
    }
}

int __wr_rm_chunk_blocking(int *var, int rm_x, int rm_y, int rm_addr, int size){
    if(__wr_rm_chunk_non_blocking(var, rm_x, rm_y, rm_addr, size))
        return -1;
    __ndma_poll();
    return 0;
}

void qemu_fprint(int type, int addr, int len){
    csrw(CSR_FPRINT_ADDR, addr);
    csrw(CSR_FPRINT_LEN, len);
    if(type == QEMU_LOG_MEM)
        asm(".word 0xbeadbeef":::);
    else if(type == QEMU_LOG_MMAB)
        asm(".word 0x8eadbeef":::);
    return;
}

int flag=0;

void enable_intr(){
    int mstatus = 8;
    _set_bit_intr_mstatus(mstatus); // enable machine intr
}

void disable_intr(){
	int mstatus = 0;
    _set_bit_intr_mstatus(mstatus); // enable machine intr
}

void enable_swi(){
    int mie = 0x8;
    _set_bit_intr_mie(mie); // enable swi intr
    return;
}

void enable_ndma(){
    int mie = 0x1000;
    _set_bit_intr_mie(mie); // enable swi intr
    return;
}

void acquire_local_lock(int lock_addr){
    int state = 1;
    do{  
        asm volatile("amoswap.w.aq %0, %0, (%1)":"+r"(state):"r"(lock_addr));
    }while(state);
}

void release_local_lock(int lock_addr){
    int state = 0;
    asm volatile("amoswap.w.rl %0, %0, (%1)":"+r"(state):"r"(lock_addr));
}



int main(int argc, char **argv)
{
	//enable_intr();
	// enable_swi();
	// enable_ndma();
    int *data1 = 0x81000000, *data2 = 0x82000000;
    
	printf("hello\n");
    
	int flag_addr = 0x80000000 + 64*1024*1024;
	int *flag = flag_addr;
	

	int hart_id;
    int result;
	asm volatile("csrr %0, mhartid":"+r"(hart_id)::);
	int addr_1 = 0x2100100;
	int *local_mem = addr_1;
	int a,b;

	if(hart_id == 1){
		printf("hart = 1\n\r");

        //case1
        // int i;
        // for(i = 0; i < 100000000; i++);
        // printf("i: %d\n\r",i);


        //case2
        // int i;
        // for(i = 0; i < 100000000; i++);
        // printf("i: %d\n\r",i);
        

        //case3
        // data1[0] = 1;
        // flag[0] = 1;

        //case4
        // int i;
        // for(i = 0; i < 100000000; i++);
        // printf("i: %d\n\r",i);

        //case5
        int i;
        for(i = 0; i < 100000000; i++);
        printf("i: %d\n\r",i);

        printf("---hart 1 ends..---\n\r");
		while(1);;

	}
	
}


int hipu_main(int argc, char **argv)
{
	int hart_id;
	asm volatile("csrr %0, mhartid":"+r"(hart_id)::);
	printf("(Huang)core id is %d\n\r", hart_id);
}
