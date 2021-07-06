import numpy as np
import re


class DnnSimLib:
    """
    DNN algorithm library
    """
    def __init__(self):
        self.fm_h = 0 #  fm height weight channel group 
        self.fm_w = 0
        self.fm_c = 0
        self.fm_g = 0
        
        self.wt_h = 0 # wt height weight channel  ? group
        self.wt_w = 0
        self.wt_c = 0
        self.wt_n = 0
        self.wt_g = 0
        
        self.pl_w = 0 # 
        self.pl_h = 0
        
        self.pad_l = 0 # pad left head right bottom
        self.pad_h = 0
        self.pad_r = 0
        self.pad_b = 0
        
        self.stride_w = 0 # stride weight height
        self.stride_h = 0
        pass

    # ======================================================
    # Parameter settings
    # ======================================================
    def set_fm_para(self, m_h, m_w, m_g, m_c):
        self.fm_h = m_h
        self.fm_w = m_w
        self.fm_g = m_g
        self.fm_c = m_c

    def set_wt_para(self, m_n, m_h, m_w, m_g, m_c):
        self.wt_n = m_n # 24  fm_och output 
        self.wt_h = m_h # 3 
        self.wt_w = m_w # 3
        self.wt_g = m_g # 1
        self.wt_c = m_c # 3   fm_ich input 

    def set_pool_para(self, m_h, m_w):
        self.pl_h = m_h
        self.pl_w = m_w

    def set_pad_para(self, m_l, m_h, m_r, m_b): # 0 0 1 1
        self.pad_l = m_l 
        self.pad_h = m_h
        self.pad_r = m_r
        self.pad_b = m_b

    def set_stride_para(self, m_h, m_w):
        self.stride_h = m_h
        self.stride_w = m_w

    def handle_round(self,data):
        data_2x_int = int(data*2.0)
        data_2x_float = data*2.0
        if data_2x_int==data_2x_float:
            return int(np.ceil(data))
        else:
            return int(np.round(data))
    # ======================================================
    # data processing functions
    # ======================================================
    def pad_fm(self, fm_np): # first call set_pad_para set param 
        """
        padding feature map according to the pad parameters.
        :param fm_np: input feature map
        :return: padded feature map
        """
        padded_h = self.fm_h + self.pad_h + self.pad_b  # head  bottom
        padded_w = self.fm_w + self.pad_l + self.pad_r  # left right
        rslt_np = np.zeros([padded_h, padded_w, self.fm_g, self.fm_c], dtype=int) # 
        for ig in range(self.fm_g):   # for group 
            for ic in range(self.fm_c): # for channel 
                for ih in range(self.fm_h): # for height 
                    temp = fm_np[ih, :, ig, ic]
                    rslt_np[ih + self.pad_h, self.pad_l : self.pad_l + self.fm_w, ig, ic] = temp # pre  0 : self.fm_w   ->  now 1 : 1 +  1+ self.fm_w [ ) 
        
        return rslt_np

    def pooling_fm(self, fm_np, type='max'):# no use 
        """
        pooling feature map
        :param fm_np: input feature map
        :param type: the type of pooling
            max: Max pooling
            min: Min pooling
            avg: average pooling
        :return: pooled feature map
        """
        #m_dest_w = (self.fm_w + self.pad_l + self.pad_r - self.pl_w)//self.stride_w + 1
        #m_dest_h = (self.fm_h + self.pad_h + self.pad_b - self.pl_h)//self.stride_h + 1
        m_dest_w = (self.fm_w + self.pad_l + self.pad_r - self.pl_w)//self.stride_w
        m_dest_h = (self.fm_h + self.pad_h + self.pad_b - self.pl_h)//self.stride_h
        data_np = np.zeros([m_dest_h, m_dest_w, self.fm_g, self.fm_c], dtype=int)
        for index_go in range(self.fm_g):
            for index_co in range(self.fm_c):
                for index_ho in range(m_dest_h):
                    ihi = index_ho * self.stride_h
                    for index_wo in range(m_dest_w):
                        iwi = index_wo * self.stride_w
                        pdata = fm_np[ihi : ihi+self.pl_h, iwi : iwi+self.pl_w, index_go, index_co]
                        if type == 'max':
                            data_np[index_ho][index_wo][index_go][index_co] = pdata.max()
                            #print(index_ho, index_wo, index_go, index_co)
                        elif type == 'min':
                            data_np[index_ho][index_wo][index_go][index_co] = pdata.min()
                        elif type == 'avg':
                            sum = pdata.sum()
                            rem = 0 if (sum % pdata.size)*2 < pdata.size else 1
                            data_np[index_ho][index_wo][index_go][index_co] = sum//pdata.size + rem
        return data_np
    

    def relu_fm(self, fm_np): # change to leaky relu
        """
        activation function: RELU
        :param fm_np: input feature map
        :return: output feature map
        """
        # TODO: add norminal activation function
        relu_np = fm_np.copy()
        relu_np[relu_np < 0] = 0
        return relu_np



    def shift_fm(self, fm_np, shift_i): # 
        """
        shift left/right to scale the data of feature map
        :param fm_np: input feature map
        :param shift_i: shift bits. shift right if value is positive, shift left if opposite.
        :return: shifted result
        """
        shape_l = fm_np.shape
        flt_np = fm_np.flatten()

        if shift_i > 0:  # round  match to  the hardware 
            shft_l = [(flt_np[i]>>shift_i) + ((flt_np[i]>>(shift_i-1)) & 0x01) for i in range(flt_np.shape[0])]
        else:
            shft_l = [(flt_np[i]<<(-shift_i)) for i in range(flt_np.shape[0])]
        shft_np = np.reshape(shft_l, shape_l)
        return shft_np

    def prot_fm(self, fm_np, precision):
        """
        limit the over flow data to MAX/MIN value.
        :param fm_np:
        :param precision:
        :return:
        """
        rslt_np = fm_np.copy()
        rslt_np[rslt_np >= (1<<(precision-1))] = (1<<(precision-1)) -1
        rslt_np[rslt_np < -(1<<(precision-1))] = -(1<<(precision-1))
        return rslt_np

    def shuffle_fm(self, fm_np):#  no use 
        """
        shuffle the feature map between the group.
        :param fm_np: input feature map
        :return: shuffled result
        """
        if fm_np.shape[0] != self.fm_g:
            grp_fm_np = np.reshape(fm_np, (self.fm_h, self.fm_w, self.fm_g, self.fm_c))
        else:
            grp_fm_np = fm_np.copy()
        grp_fm_np = grp_fm_np.transpose((0, 1, 3, 2))
        return np.reshape(grp_fm_np, (self.fm_h, self.fm_w, self.fm_g, self.fm_c))

    def conv(self, fm_np, wt_np):
        """
        make convolution operation.
        :param fm_np: input feature map
        :param wt_np: input weight
        :return: the result of convolution
        """
        # TODO: add dilating operation                           # self.wt_n = 24 output num = 24    
        assert self.fm_g == self.wt_g and self.fm_c == self.wt_c # self.wt_c input map num = 3
        # calculate the dimensions of result.
        # more strict condition: assert (self.fm_w + self.pad_l + self.pad_r - self.wt_w) % self.stride_w == 0
        m_dest_w = (self.fm_w + self.pad_l + self.pad_r - self.wt_w) // self.stride_w + 1 # (640 + 0 + 1 - 3)//2 + 1 = 320
        # more strict condition: assert (self.fm_h + self.pad_h + self.pad_b - self.wt_h) % self.stride_h == 0
        m_dest_h = (self.fm_h + self.pad_h + self.pad_b - self.wt_h) // self.stride_h + 1 # (360 + 0 + 1 - 3)//2 + 1 = 180

        rslt_np = np.zeros([m_dest_h, m_dest_w, self.fm_g, self.wt_n], dtype=int) # [180 320 1 24 ]

        for index_g in range(self.fm_g):  # 1
            for index_co in range(self.wt_n): # 24
                for index_ho in range(m_dest_h): # 180 
                    index_hi = index_ho * self.stride_h # 0-179 -> * 2
                    for index_wo in range(m_dest_w): # 320
                        index_wi = index_wo * self.stride_w # 0-319 -> *2 
                        # accumulate convolution

                        ifm_array = fm_np[index_hi:index_hi+self.wt_h, index_wi:index_wi+self.wt_w, index_g, :].flatten()
                        iwt_array = wt_np[index_co, ..., index_g, : ].flatten()
                        #iwt_array = wt_np[..., index_g, : ,index_co].flatten()

                        psum = np.dot(ifm_array, iwt_array)
                        # add bias
                        # psum += bias_np[index_g][index_co]
                        rslt_np[index_ho][index_wo][index_g][index_co] = psum
                        '''
                        if(index_g==0 and index_co==0 and index_ho==0 and index_wo==0):
                            print('zbr',fm_np.shape)
                            print(ifm_array,iwt_array,psum)
                            abc
                        '''
                           
                        # if index_g == 0 and index_co == 0 and index_ho == 0 and index_wo == 0:
                        #     print("Loop priorityis HWC.")
                        #     print("Input img is:\n", fm_np[0:3, 0:3, 0, 0:3])
                        #     print("The corresponding weight is:\n", wt_np[0:3, 0:3, 0, 0:3])
                        #     print("Dot-multiply Psum result is:\n", psum)
        # return convolution result
        return rslt_np

    def dwconv(self, fm_np, wt_np): # no use 
        """
        depth-wise convolution operation.
        :param fm_np: input feature map
        :param wt_np: input weight
        :return: the result of depth-wise convolution
        """
        m_dest_w = (self.fm_w + self.pad_l + self.pad_r - self.wt_w)//self.stride_w + 1
        m_dest_h = (self.fm_h + self.pad_h + self.pad_b - self.wt_h)//self.stride_h + 1
        data_np = np.zeros([m_dest_h, m_dest_w, self.fm_g, self.fm_c], dtype=int)
        for index_go in range(self.fm_g):
            for index_co in range(self.fm_c):
                for index_ho in range(m_dest_h):
                    ihi = index_ho * self.stride_h
                    for index_wo in range(m_dest_w):
                        iwi = index_wo * self.stride_w
                        ifm_array = fm_np[ihi : ihi+self.wt_h, iwi : iwi+self.wt_w, index_go, index_co].flatten()
                        iwt_array = wt_np[0, : , : , index_go, index_co].flatten()

                        sum = np.dot(ifm_array, iwt_array)
                        data_np[index_ho][index_wo][index_go][index_co] = sum
        return data_np

    def add_bias(self, fm_np, bias_np):
        """
        add bias to feature map.
        :param fm_np:
        :param bias_np:
        :return:
        """
        assert bias_np.shape[0] == self.fm_g # 1
        assert bias_np.shape[1] == self.fm_c # 1

        rslt_np = fm_np.copy()
        for index_g in range(self.fm_g):
            for index_c in range(self.fm_c):
                rslt_np[:, :, index_g, index_c] += bias_np[index_g, index_c]
        return rslt_np

    def cmp_fm(self, fm_np, expect_np):
        """
        compare fm and expect fm, print the different element
        :param fm_np: fm0 in numpy format
        :param expect_np: fm1 in numpy format
        :return: None
        """
        return 0,0,0,0
        print('Comparing...')
        height, width,grp, chl  = fm_np.shape
        for ig in range(grp):
            for ic in range(chl):
                for ih in range(height):
                    for iw in range(width):
                        expect_val = expect_np[ih, iw, ig, ic]
                        actual_val = fm_np[ih, iw, ig, ic]
                        if expect_val != actual_val:
                            print("fm[%d][%d][%d][%d] is actually 0x%0x," % (ih, iw, ig, ic, actual_val)),
                            print("while the expectation of which is 0x%0x" % expect_val)
                            return ih, iw, ig, ic
        return -1,-1,-1,-1
    
    #################################################################
    #yolov3 add functions
    #################################################################

    def lrelu_fm(self, fm_np, alpha=0.1): # change to leaky relu
        """
        activation function: RELU
        :param fm_np: input feature map
        :return: output feature map
        """
        # TODO: add norminal activation function
 

        relu_np = fm_np.copy()
        for index_h in range(self.fm_h):
            for index_w in range(self.fm_w):
                for index_g in range(self.fm_g):
                    for index_c in range(self.fm_c):
                        pos_tmp = relu_np[index_h, index_w, index_g, index_c]
                        neg_tmp = relu_np[index_h, index_w, index_g, index_c] * alpha
                        neg_tmp = self.handle_round(neg_tmp)
                        pos_tmp = self.handle_round(pos_tmp)
                        relu_np[index_h, index_w, index_g, index_c] = pos_tmp if pos_tmp > 0 else neg_tmp

        return relu_np

    def add_fm(self, fm_np_a, fm_np_b):
        """
        add each point of a   to each  point of b   fm_np_add = fm_np_a = fm_np_b
        :param fm_np_a: adder source a
        :param fm_np_b: adder source a
        :return: fm_np_add
        """
        sa = np.shape(fm_np_a)
        sb = np.shape(fm_np_b)
        assert(fm_np_a.ndim == 4)
        assert(sa==sb)
        fm_np_add = np.zeros(sa,dtype=np.int32)
        height, width , grp, chl = fm_np_a.shape
        for ih in range(height):
            for iw in range(width):
                for ig in range(grp):
                    for ic in range(chl):
                        fm_np_add[ih, iw ,ig, ic,] = int(fm_np_a[ih, iw ,ig, ic,] + fm_np_b[ih, iw ,ig, ic])
        #fm_np_add = fm_np_a + fm_np_b
        
        return fm_np_add  
    def cat_fm(self, fm_np_a, fm_np_b):
        """
        cat fm a to b -> fm cat   a is the first place at cat
        :param fm_np_a: cat source a
        :param fm_np_b: cat source b
        :return: fm_np_cat
        """
        sa = np.shape(fm_np_a)
        sb = np.shape(fm_np_b)
        print('fm_a shape',sa)
        print('fm_a shape',sb)
        assert(fm_np_a.ndim == 4 and fm_np_b.ndim == 4)
        assert(sa[:-1]==sb[:-1])
    
        fm_np_cat = np.zeros([ sa[0], sa[1], sa[2], sa[3]+sb[3] ],dtype=np.int32)
    
        fm_np_cat = np.concatenate((fm_np_a,fm_np_b),axis=3)
        
        return fm_np_cat  

    def upsample_nst_ngr(self, fm_np):
        """
        compare fm and expect fm, print the different element
        :param fm_np: fm0 in numpy format
        :param expect_np: fm1 in numpy format
        :return: None
        """
        assert(fm_np.ndim == 4)
        sa = np.shape(fm_np)
        print('pre up',sa)
        fm_np_ups = np.zeros([ sa[0]*2, sa[1]*2, sa[2], sa[3] ],dtype=np.int32)
    
        height, width , grp, chl = fm_np.shape
        for ih in range(height):
            for iw in range(width):
                fm_np_ups[ih*2  , iw*2  ,:, :,] = fm_np[ih, iw ,:, :,] 
                fm_np_ups[ih*2+1, iw*2  ,:, :,] = fm_np[ih, iw ,:, :,] 
                fm_np_ups[ih*2  , iw*2+1,:, :,] = fm_np[ih, iw ,:, :,] 
                fm_np_ups[ih*2+1, iw*2+1,:, :,] = fm_np[ih, iw ,:, :,] 
        
        return fm_np_ups 

    # ======================================================
    # File read/write operations
    # ======================================================
    def read_hex_from_file(self, file_name, precision=8):
        """
        read unified data from filesystem, where the data is treated as hex ascii format
        :param file_name: the file_dir + file_name
        :param precision: the precision of hex data
        :return: read data in numpy array format
        """
        with open(file_name, 'rt') as infile:  # type: BinaryIO
            hex_array_l = infile.readlines()
        data_array_a = np.array([int(i, 16) for i in hex_array_l])
        max = 1<<precision
        data_array_a[data_array_a >= (1<<(precision-1))] = data_array_a[data_array_a >= (1<<(precision-1))] - max # >=  128  then  -256 
        return np.array(data_array_a)

    def write_hex_to_file(self, file_name, data_a, precision=8):
        """
        write unified data to filesystem, with hex ascii format
        :param file_name: the file_dir + file_name
        :param data_array_np: the source data that will write to filesystem
        :param precision: the precision of hex data
        :return: None
        """
        data2_a = data_a.copy()
        data2_a[data_a < 0] += 1 << precision
        with open(file_name, 'wt') as outfile:  # type: BinaryIO
            for data_i in data2_a:
                hex_s = ('%0'+str((precision+3)//4)+'x') % int(data_i)
                outfile.write(hex_s+'\n')

    def trans_parallel(self, in_file_name, out_filename, para_in, para_out):
        """
        transform the data parallel of input data.
        :param in_file_name: input file name
        :param out_filename: output file name
        :param para_in: the parallel of input file
        :param para_out: the parallel of output file
        :return: None
        """
        with open(in_file_name, 'rt') as infile: #type: BinaryIO
            input_l = infile.readlines()
        output_l = ['' for i in range(len(input_l) * para_in // para_out)]
        j = 0
        for i in range(len(input_l)):
            for ii in range(para_in):
                div_str = input_l[i][ii*2 : ii*2+2]
                output_l[j//para_out] += div_str
                j += 1
        with open(out_filename, 'wt') as outfile: #type: BinaryIO
            for data_o in output_l:
                outfile.write(data_o + '\n')

    def read_fm(self, file_name, precision, stype='hex'):
        """
        read feature map from filesystem
        :param file_name: the file_dir + file_name
        :param precision: the precision of the data
        :param stype: source file type, described as below:
            'circuit': data format is FPGA circuit;
            'hex': data format is HWNC in hex;
            'dec': data format is HWNC in dec;
            'npy': data format is numpy format.
        :return: read data
        """
        if stype == 'circuit' or stype == 'hex':
            fm_a = self.read_hex_from_file(file_name, precision)
            if(fm_a.size != self.fm_h * self.fm_w * self.fm_g * self.fm_c):
                print('file line , require',fm_a.size,self.fm_h * self.fm_w * self.fm_g * self.fm_c)
            assert fm_a.size == self.fm_h * self.fm_w * self.fm_g * self.fm_c
            if stype == 'circuit':
                fm_a = self.trans_fmcirc_to_fm(fm_a)
            fm_np = fm_a.reshape([self.fm_h, self.fm_w, self.fm_g, self.fm_c])  # h=360     w=640    g=1   ich=3
            
            return fm_np
        elif stype == 'dec':
            # TODO: implement reading file in dec type
            pass
        elif stype == 'npy':
            # TODO: implement reading file in numpy type
            pass
        else:
            print('[ERROR]: Cannot recognize indicated source type.')

    def write_fm(self, file_name, fm_np, precision, dtype='hex', fm_type='ch8'):
        """
        write feature map to filesystem
        :param file_name: the file_dir + file_name
        :param fm_np: the input feature map
        :param precision: the precision of the data
        :param dtype: source file type, described as below:
            'circuit': data format is FPGA circuit;
            'hex': data format is HWNC in hex;
            'dec': data format is HWNC in dec;
            'npy': data format is numpy format.
        :return: None
        """
        if dtype == 'hex' or dtype == 'circuit':
            if dtype == 'circuit':
                fm_a = self.trans_fm_to_fmcirc(fm_np, fm_type)
            else:
                fm_a = fm_np.flatten()
            self.write_hex_to_file(file_name, fm_a, precision)
        elif dtype == 'dec':
            # TODO: implement reading file in dec type
            pass
        elif dtype == 'npy':
            # TODO: implement reading file in numpy type
            pass
        else:
            print('[ERROR]: Cannot recognize indicated destination type.')

    def read_wt(self, file_name, precision, stype='hex'):
        """
        read weight data from filesystem
        :param file_name: the file_dir + file_name
        :param precision: the precision of the data
        :param stype: source file type, described as below:
            'circuit': data format is FPGA circuit;
            'hex': data format is NHWC in hex;
            'dec': data format is NHWC in dec;
            'npy': data format is numpy format.
        :return: read data
        """
        if stype == 'hex' or stype == 'circuit':
            wt_a = self.read_hex_from_file(file_name, precision)
            if(wt_a.size != self.wt_h * self.wt_w * self.wt_c * self.wt_g * self.wt_n):
                print('file line , require',wt_a.size,self.wt_h*self.wt_w*self.wt_c*self.wt_n)
            assert wt_a.size == self.wt_h * self.wt_w * self.wt_c * self.wt_g * self.wt_n
            if stype == 'circuit':
                wt_a = self.trans_wtcirc_to_wt(wt_a)
            
            #wt_a = wt_a.reshape([self.wt_h, self.wt_w, self.wt_c, self.wt_n])  # h  w  cin cout
            ##wt_np = wt_a.reshape([self.wt_n, self.wt_h, self.wt_w, self.wt_c])
            
            #wt_a = np.transpose(wt_a,[3,0,1,2])
            
            #wt_np = wt_a[:,:,:,np.newaxis,:]
            
            #wt_np = wt_a.reshape([self.wt_n, self.wt_h, self.wt_w, self.wt_g, self.wt_c])  # och  h  w   c(no use =1)   ich
            return wt_a
        elif stype == 'dec':
            # TODO: implement reading file in dec type
            pass
        elif stype == 'npy':
            # TODO: implement reading file in numpy type
            pass
        else:
            print('[ERROR]: Cannot recognize indicated source type.')

    def write_wt(self, file_name, wt_np, precision, dtype='hex', type = 'dwc'):
        """
        write weight data to filesystem
        :param file_name: the file_dir + file_name
        :param wt_np: the input weight data
        :param precision: the precision of the data
        :param dtype: source file type, described as below:
            'circuit': data format is FPGA circuit;
            'hex': data format is NHWC in hex;
            'dec': data format is NHWC in dec;
            'npy': data format is numpy format.
        :param type: 'dwc' is depth-wise convlolution; 'conv' is normal convlution
        :return: None
        """
        if dtype == 'hex' or dtype == 'circuit':
            if dtype == 'circuit':
                wt_np = self.trans_wt_to_wtcirc(wt_np, type)
            wt_a = wt_np.flatten()
            self.write_hex_to_file(file_name, wt_a, precision)
        elif dtype == 'dec':
            # TODO: implement reading file in dec type
            pass
        elif dtype == 'npy':
            # TODO: implement reading file in numpy type
            pass
        else:
            print('[ERROR]: Cannot recognize indicated destination type.')

    def read_bias(self, file_name, precision, dtype='hex', type='conv'):
        """
        load bias parameters
        :param file_name: the file_dir + file_name
        :param precision: the precision of the data
        :param dtype: source file type, described as below:
            'circuit': data format is FPGA circuit;
            'hex': data format is NHWC in hex;
            'dec': data format is NHWC in dec;
            'npy': data format is numpy format.
        :return: bias data
        """
        if dtype == 'hex':
            bias_a = self.read_hex_from_file(file_name, precision)
        elif dtype == 'dec':
            bias_a = self.read_hex_from_file(file_name, precision)
            # TODO: implement reading file in numpy type
            pass
        elif dtype == 'npy':
            bias_a = self.read_hex_from_file(file_name, precision)
            # TODO: implement reading file in numpy type
            pass
        else:
            print('[ERROR]: Cannot recognize indicated destination type.')
            return

        if type == 'dwc':
            bias_np = bias_a.reshape([self.wt_g, self.wt_c])
        else:
            bias_np = bias_a.reshape([self.wt_g, self.wt_n])

        return bias_np

    def write_bias(self, file_name, bias_np, precision, dtype='hex'):
        """
        save bias parameters
        :param file_name: the file_dir + file_name
        :param bias_np: the input biase data
        :param precision: the precision of the data
        :param dtype: source file type, described as below:
            'circuit': data format is FPGA circuit;
            'hex': data format is NHWC in hex;
            'dec': data format is NHWC in dec;
            'npy': data format is numpy format.
        :return: None
        """
        bias_a = bias_np.flatten()
        if dtype == 'hex' or dtype == 'circuit':
            self.write_hex_to_file(file_name, bias_a, precision)
        elif dtype == 'dec':
            # TODO: implement reading file in numpy type
            pass
        elif dtype == 'npy':
            # TODO: implement reading file in numpy type
            pass
        else:
            print('[ERROR]: Cannot recognize indicated destination type.')
            return

    def read_prop(self, file_name):
        """
        read the parameters of proposal box
        :param file_name:
        :return:
        """
        with open(file_name, 'rt') as infile:
            content = infile.readlines()
            prop = []
            for index in range(content.len/6):
                x = re.findall('\d+', content[index*6 + 1])
                w = re.findall('\d+', content[index*6 + 2])
                y = re.findall('\d+', content[index*6 + 3])
                h = re.findall('\d+', content[index*6 + 4])
                prop.append((x, w, y, h))
        return prop

    # ======================================================
    # data format transform
    # ======================================================
    def  trans_fmcirc_to_fm(self, fm_array):
        """
        transform the format of feature map from FPGA circuit to HWNC
        :param fm_array: FPGA array feature map
        :return:  feature map in HWNC format
        """
        assert self.fm_w % 8 == 0
        fm_np = np.zeros((self.fm_h, self.fm_w, self.fm_g, self.fm_c), dtype=int)
        index = 0
        for ig in range(self.fm_g):
            for ih in range(self.fm_h):
                for iiw in range(self.fm_w // 8):
                    for iic in range(self.fm_c // 8):
                        for iw in range(8):
                            for ic in range(8):
                                fm_np[ih][iiw+iw*self.fm_w//8][ig][iic*8+ic] = fm_array[index]
                                index += 1
        return fm_np

    def trans_fm_to_fmcirc(self, fm_np, fm_type='ch8'):
        """
        transform the format of feature map from NHWC to FPGA circuit format
        :param fm_np: input orignal feature map
        :return: feature map in FPGA circuit format
        """
        index = 0
        fmcirc_l = [0 for i in range (self.fm_g*self.fm_h*self.fm_w*self.fm_c) ]
        if fm_type == 'ch8':
            assert self.fm_w % 8 == 0
            for ih in range(self.fm_h):
                for iiw in range(self.fm_w // 8):
                    for ig in range(self.fm_g):
                        for iic in range(self.fm_c // 8):
                            for iw in range(8):
                                for ic in range(8):
                                    fmcirc_l[index] = fm_np[ih][iiw+iw*self.fm_w//8][ig][iic*8+ic]
                                    index += 1
        else:
            assert self.fm_c % 64 == 0
            for ih in range(self.fm_h):
                for iw in range(self.fm_w):
                    for ig in range(self.fm_g):
                        for iic in range(self.fm_c // 64):
                            for ic in range(64):
                                fmcirc_l[index] = fm_np[ih][iw][ig][iic*64+ic]
                                index += 1
        return np.array(fmcirc_l)

    def trans_wtcirc_to_wt(self, wt_array):
        """
        transform the format of weight from FPGA logic format to NCHW
        :param wt_array: input FPGA logic weight
        :return: weight in original format
        """
        wt_np = np.zeros((self.wt_n, self.wt_h, self.wt_w, self.wt_g, self.wt_c), dtype=int)
        index = 0
        for iiwn in range(int(self.wt_n/8)):
            for iwh in range(self.wt_h):
                for iww in range(self.wt_w):
                    for iwg in range(self.wt_g):
                        for iiwc in range(int(self.wt_c/8)):
                            for iwn in range(8):
                                for iwc in range(8):
                                    wt_np[iiwn*8+iwn][iwh][iww][iwg][iiwc*8+iwc] = wt_array[index]
                                    index += 1
        return wt_np

    def trans_wt_to_wtcirc(self, wt_np, wt_type = 'ch8', type = 'dwc'):
        """
        transform the format of weight from NCHW to FPGA circuit format
        :param wt_np: input original weight
        :param type: 'dwc' is depth-wise convolution; 'conv' is normal convlution
        :return: weight in FPGA circuit format
        """
        index = 0
        if wt_type == 'ch8':
            if type == 'dwc':
                wtcirc_l = [0 for i in range(self.wt_g * self.wt_n * self.wt_h * self.wt_w * self.wt_c * 8)]
                for iwh in range(self.wt_h):
                    for iww in range(self.wt_w):
                        for iwg in range(self.wt_g):
                            for iiwc in range(int(self.wt_c/8)):
                                for irp in range(8):
                                    for iwc in range(8):
                                        wtcirc_l[index] = wt_np[0][iwh][iww][iwg][iiwc*8+iwc]
                                        index += 1
            else:
                wtcirc_l = [0 for i in range(self.wt_g * self.wt_n * self.wt_h * self.wt_w * self.wt_c)]
                for iiwn in range(int(self.wt_n/8)):
                    for iwh in range(self.wt_h):
                        for iww in range(self.wt_w):
                            for iwg in range(self.wt_g):
                                for iiwc in range(int(self.wt_c/8)):
                                    for iwn in range(8):
                                        for iwc in range(8):
                                            wtcirc_l[index] = wt_np[iiwn*8+iwn][iwh][iww][iwg][iiwc*8+iwc]
                                            index += 1
        else:
            if type == 'dwc':
                wtcirc_l = [0 for i in range(self.wt_g * self.wt_n * self.wt_h * self.wt_w * self.wt_c)]
                for iwh in range(self.wt_h):
                    for iww in range(self.wt_w):
                        for iwg in range(self.wt_g):
                            for iiwc in range(int(self.wt_c / 64)):
                                for iwc in range(64):
                                    wtcirc_l[index] = wt_np[0][iwh][iww][iwg][iiwc * 64 + iwc]
                                    index += 1
            else:
                wtcirc_l = [0 for i in range(self.wt_g * self.wt_n * self.wt_h * self.wt_w * self.wt_c)]
                for iiwc in range(8):
                    for iiwn in range(int(self.wt_n / 8)):
                        for iwh in range(self.wt_h):
                            for iww in range(self.wt_w):
                                for iwg in range(self.wt_g):
                                    for iiiwc in range(int(self.wt_c / 64)):
                                        for iwn in range(8):
                                            for iwc in range(8):
                                                wtcirc_l[index] = wt_np[iiwn * 8 + iwn][iwh][iww][iwg][iiiwc * 64 + iiwc * 8 + iwc]
                                                index += 1

        return np.array(wtcirc_l)

    def trans_bias_to_biascirc(self, bias_np, bias_type = 'ch8', type = 'dwc'):
        """
        transform the format of bias from C to FPGA circuit format
        :param bias_np: input original bias data
        :param type: 'dwc' is depth-wise convolution; 'conv' is normal convlution
        :return: bias in FPGA circuit format
        """
        index = 0
        if bias_type == 'ch8':
            if type == 'dwc':# have not change to 4B bieas
                biascirc_l = [0 for i in range(self.wt_g * self.wt_c * 8)]
                for iwg in range(self.wt_g):
                    for iiwc in range(int(self.wt_c/8)):
                        for irp in range(2): # change 8 ->2
                            for iwc in range(8):
                                biascirc_l[index] = bias_np[iwg][iiwc*8+iwc]
                                index += 1 
            else:
                biascirc_l = [0 for i in range(self.wt_g * self.wt_n * 8)]# change to 4B bias
                for iwg in range(self.wt_g):
                    for iiwn in range(int(self.wt_n/8)):
                        for irp in range(2): # change 8 ->2
                            for iwn in range(8):                                
                                biascirc_l[index] = bias_np[iwg][iiwn*8+iwn] & 0xff 
                                index += 1
                                biascirc_l[index] = (bias_np[iwg][iiwn*8+iwn] >> 8) & 0xff 
                                index += 1 
                                biascirc_l[index] = (bias_np[iwg][iiwn*8+iwn] >> 16) & 0xff 
                                index += 1 
                                biascirc_l[index] = (bias_np[iwg][iiwn*8+iwn] >> 24) & 0xff 
                                index += 1
                                
                                

                                                              
        else:
            if type == 'dwc': # have not change to 4B bieas
                biascirc_l = [0 for i in range(self.wt_g * self.wt_c)]
                for iwg in range(self.wt_g):
                    for iiwc in range(int(self.wt_c/64)):
                        for iwc in range(64):
                            biascirc_l[index] = bias_np[iwg][iiwc*64+iwc]
                            index += 1
            else:
                biascirc_l = [0 for i in range(self.wt_g * self.wt_n * 8)] # change to 4B bias
                for iwg in range(self.wt_g):
                    for iiwn in range(int(self.wt_n/8)):
                        for irp in range(2): # change 8 ->2
                            for iwn in range(8):
                                biascirc_l[index] = bias_np[iwg][iiwn*8+iwn] & 0xff 
                                index += 1
                                biascirc_l[index] = (bias_np[iwg][iiwn*8+iwn] >> 8) & 0xff 
                                index += 1 
                                biascirc_l[index] = (bias_np[iwg][iiwn*8+iwn] >> 16) & 0xff 
                                index += 1 
                                biascirc_l[index] = (bias_np[iwg][iiwn*8+iwn] >> 24) & 0xff 
                                index += 1

        return np.array(biascirc_l)
    def write_fm_ch64(self, file_name, fm_np, precision, dtype='hex', fm_type='ch8'):
        """
        write feature map to filesystem
        :param file_name: the file_dir + file_name
        :param fm_np: the input feature map
        :param precision: the precision of the data
        :param dtype: source file type, described as below:
            'circuit': data format is FPGA circuit;
            'hex': data format is HWNC in hex;
            'dec': data format is HWNC in dec;
            'npy': data format is numpy format.
        :return: None
        """
        if dtype == 'hex' or dtype == 'circuit':
            if dtype == 'circuit':
                fm_a = self.trans_fm_to_fmcirc_ch64(fm_np, fm_type)
            else:
                fm_a = fm_np.flatten()
            self.write_hex_to_file(file_name, fm_a, precision)
        elif dtype == 'dec':
            # TODO: implement reading file in dec type
            pass
        elif dtype == 'npy':
            # TODO: implement reading file in numpy type
            pass
        else:
            print('[ERROR]: Cannot recognize indicated destination type.')

    def trans_fm_to_fmcirc_ch64(self, fm_np, fm_type='ch8'):
        """
        transform the format of feature map from NHWC to FPGA circuit format
        :param fm_np: input orignal feature map
        :return: feature map in FPGA circuit format
        """
        index = 0
        fmcirc_l = [0 for i in range (self.fm_g*self.fm_h*self.fm_w*self.fm_c) ]
        if fm_type == 'ch8':
            assert self.fm_w % 8 == 0
            for ih in range(self.fm_h):
                for iiw in range(self.fm_w // 8):
                    for ig in range(self.fm_g):
                        for iw in range(8):
                            for iic in range(self.fm_c // 8):
                                for ic in range(8):
                                    fmcirc_l[index] = fm_np[ih][iiw+iw*self.fm_w//8][ig][iic*8+ic]
                                    index += 1
        else:
            assert self.fm_c % 64 == 0
            for ih in range(self.fm_h):
                for iw in range(self.fm_w):
                    for ig in range(self.fm_g):
                        for iic in range(self.fm_c // 64):
                            for ic in range(64):
                                fmcirc_l[index] = fm_np[ih][iw][ig][iic*64+ic]
                                index += 1
        return np.array(fmcirc_l)

if __name__ == "__main__":
    m_dnnsimlib = DnnSimLib()
    m_dnnsimlib.set_fm_para(1, 8, 4, 6)
    m_dnnsimlib.set_wt_para(2, 1, 8, 3, 3)
    m_dnnsimlib.set_pad_para(2, 2, 1, 1)
    m_dnnsimlib.set_stride_para(2, 2)

    m_fm = np.ones([1, 8, 4, 6])
    print("The shape of initial feature map is:"),
    print(m_fm.shape)
    m_pad_fm = m_dnnsimlib.pad_fm(m_fm)
    print("The shape of padded feature map is:"),
    print(m_pad_fm.shape)
    print("Padded feature map is:")
    print(m_pad_fm)

    m_wt = np.ones([2, 1, 8, 3, 3])
    print("Weight is:")
    print(m_wt)

    m_bias = np.zeros([1, 2])
    print("Bias is:")
    print(m_bias)

    m_rslt = m_dnnsimlib.conv(m_pad_fm, m_wt)
    print("Convolution result is:")
    print(m_rslt)
