# -*- coding: utf-8 -*-
import numpy as np
import re
import DnnSimLib as dnnlib
import os

'''
def write_fm_to_file(file_path, fm_np, precision, fm_type, en_org=False,  en_circuit=False, en_paral=False):
    if en_org:
        dnn.write_fm(file_path + '.txt', fm_np, precision, fm_type = fm_type)#
    if en_circuit:
        dnn.write_fm(file_path + '_fpga.txt', fm_np, precision, 'circuit', fm_type = fm_type)#
    if en_paral:
        dnn.trans_parallel(file_path+'_fpga.txt', file_path+'_fpga_paral8.txt', 1, 8)
        dnn.trans_parallel(file_path+'_fpga.txt', file_path+'_fpga_paral64.txt', 1, 64)
'''

#
# featuremap: Height Width Channel
# weight    : kernel_num Height Width Channel
# bias 		: Channel
#
if __name__ == "__main__":
    ifm_name = './data/ifm.txt'
    wt1_name = './data/wt1.txt'
    bias1_name = './data/bias1.txt'
    # wt2_name = '../../clib/example/runtime/data/wt2.txt'
    ofm_name = './output/ofm3.txt'

    dnn = dnnlib.DnnSimLib() 

    # set input shape fm_h, fm_w, fm_g, fm_ich
    dnn.set_fm_para(5, 32, 1, 16) 
    ifm_np = dnn.read_fm(ifm_name, 8, 'circuit')
    
    dnn.set_wt_para(16, 3, 3, 1, 16)
    wt_np1 = dnn.read_wt(wt1_name, 8, 'circuit')

    bias_np1 = dnn.read_bias(bias1_name, 32, type='conv') 

    # set pad/stride param
    dnn.set_pad_para(1, 1, 1, 1)
    dnn.set_stride_para(1, 1)

    # conv1
    ifm_pad_np = dnn.pad_fm(ifm_np)
    ofm_np = dnn.conv(ifm_pad_np, wt_np1)
    ofm_np = dnn.add_bias(ofm_np, bias_np1)
    ofm_np = dnn.shift_fm(ofm_np, 0)
    # ofm_np = dnn.prot_fm(ofm_np, 8)
    
    # conv2
    # dnn.set_fm_para(5, 32, 1, 16)
    # ofm_pad_np = dnn.pad_fm(ofm_np)
    # conv_np = dnn.conv(ofm_pad_np, wt_np2)
    # ofm_np = dnn.shift_fm(conv_np, 12)
    # ofm_np = dnn.prot_fm(ofm_np, 8)

    # set ofm shape and wrtie back
    dnn.set_fm_para(5, 32, 1, 16)
    dnn.write_fm(ofm_name, ofm_np, 32, 'circuit', 'ch8')
    # dnn.write_fm(ofm_name, ofm_np, 32, 'circuit', 'ch64') 
