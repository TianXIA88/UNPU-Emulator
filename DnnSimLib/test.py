# -*- coding: utf-8 -*-
import numpy as np
import re
import DnnSimLib as dnnlib
def write_fm_to_file(file_path, fm_np, precision, fm_type, en_org=False,  en_circuit=False, en_paral=False):
    if en_org:
        dnn.write_fm(file_path + '.txt', fm_np, precision, fm_type = fm_type)#
    if en_circuit:
        dnn.write_fm(file_path + '_fpga.txt', fm_np, precision, 'circuit', fm_type = fm_type)#
    if en_paral:
        dnn.trans_parallel(file_path+'_fpga.txt', file_path+'_fpga_paral8.txt', 1, 8)
        dnn.trans_parallel(file_path+'_fpga.txt', file_path+'_fpga_paral64.txt', 1, 64)
#
# featuremap:Height Width Channel
# weight	 : kernel_num Height Width Channel
# bias 		: Channel
if __name__ == "__main__":
    ifm_name = '/home/jingwen/hipu_qemu/riscv-hipu-probe/ifm.txt'
    wt_name1 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/wt1.txt'
    wt_name2 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/wt2.txt'
    wt_name3 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/wt3.txt'
    wt_name4 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/wt4.txt'
    bias_name1 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/bias1.txt'
    bias_name2 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/bias2.txt'
    bias_name3 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/bias3.txt'
    bias_name4 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/bias4.txt'
    ofm_name = '/home/jingwen/hipu_qemu/riscv-hipu-probe/ofm.txt'
    ofm_name1 = '/home/jingwen/hipu_qemu/riscv-hipu-probe/ofm1.txt'
    
    dnn = dnnlib.DnnSimLib() 
    dnn.set_fm_para(32, 32, 1, 8) # set input shape 
    # read data -> shape to fm_h, fm_w, fm_g, fm_ich
    ifm_np = dnn.read_fm(ifm_name, 8, 'circuit') # 
    #dnn.write_fm(ofm_name, ifm_np, 8, 'circuit', 'ch8')
    dnn.set_wt_para(8, 3, 3, 1, 8)
    wt_np1 = dnn.read_wt(wt_name1, 8, 'circuit')#
    #dnn.write_wt(ofw_name, wt_np, 8, 'circuit')
    
    bias_np1 = dnn.read_bias(bias_name1, 32, type='conv') #to edit

    #conv1
    dnn.set_pad_para(1, 1, 1, 1) # #1111
    ifm_pad_np = dnn.pad_fm(ifm_np)
    dnn.set_stride_para(1, 1)#
    conv_np = dnn.conv(ifm_pad_np, wt_np1)#

    ofm_np = dnn.add_bias(conv_np, bias_np1)
    ofm_np = dnn.shift_fm(ofm_np, 12)
    ofm_np = dnn.prot_fm(ofm_np, 8)

    #pooling1
    dnn.set_stride_para(2, 2)#
    dnn.set_fm_para(32, 32, 1, 8)
    dnn.set_pool_para(2,2)
    ofm_np = dnn.pooling_fm(ofm_np, 'max')

    #conv2
    dnn.set_fm_para(16, 16, 1, 8) # set input shape 
    dnn.set_wt_para(64, 3, 3, 1, 8)
    wt_np2 = dnn.read_wt(wt_name2, 8, 'circuit')#
    bias_np2 = dnn.read_bias(bias_name2, 32, type='conv') #to edit

    dnn.set_pad_para(1, 1, 1, 1) # #1111
    ifm_pad_np = dnn.pad_fm(ofm_np)
    dnn.set_stride_para(1, 1)#
    conv_np = dnn.conv(ifm_pad_np, wt_np2)#
    dnn.set_fm_para(16, 16, 1, 64)
    ofm_np = dnn.add_bias(conv_np, bias_np2)
    ofm_np = dnn.shift_fm(ofm_np, 12)
    ofm_np = dnn.prot_fm(ofm_np, 8)

 #pooling2
    dnn.set_stride_para(2, 2)#
    dnn.set_fm_para(16, 16, 1, 64)
    dnn.set_pool_para(2,2)
    ofm_np = dnn.pooling_fm(ofm_np, 'max')

    dnn.set_fm_para(8, 8, 1, 64)
    # dnn.set_fm_para(32, 32, 1, 8)
    #dnn.write_fm(ofm_name, conv_np, 32, 'hex', 'ch8') ##
    dnn.write_fm(ofm_name, ofm_np, 32, 'circuit', 'ch8')
    #dnn.write_wt(wt_name, wt_np, 8, 'circuit', 'conv')
