import os
import sys
import pprint
# import numpy as np


class CodeWriter:

    # ArithCMD2ASM = {
    #     'add' : "ADD",
    #     'sub' : "SUB",
    #     'and' : "",
    #     'or'  : "ADD",
    #     'not' : "ADD",
    #     'eq'  : "ADD",
    #     'lt'  : "ADD",
    #     'gt'  : "ADD",
    #     'neg' : "ADD",        
    # }
    ram_base_addr = {
        "reg"    : 0x0,    # 0x0    ~ 0xf, for 16 registers
        "static" : 0x10,   # 0x10   ~ 0xff, for static
        "stack"  : 0x100,  # 0x100  ~ 0x7ff, for stack
        "heap"   : 0x800,  # 0x800  ~ 0x3fff, for heap
        "mmio"   : 0x4000, # 0x4000 ~ 0x5fff, for MMIO
        "unused" : 0x6000  # 0x6000 ~ 0x7fff, unused        
    }

    reg = {
        "SP"     : 0x0,  # Stack Pointer
        "LCL"    : 0x1,  # BaseAddr of local segment
        "ARG"    : 0x2,  # BaseAddr of argument segment
        "THIS"   : 0x3,  # BaseAddr of this segment in heap
        "THAT"   : 0x4,  # BaseAddr of that segment in heap
        "temp"   : 0x5,  # 0x5~0xc for store temp segment value
        "general" : 0xd  # 0xd~0xf can use as general register
    }
    
    def __init__(self, file):
        self.fp = open(file, mode='w')
        # self.ram = [0] * 0x7fff
        
        # register
        self.sp = self.ram_base_addr["stack"]
        
        return 

    def add_asmcode_init_sp(self, asmcode_list):
        self.sp = self.ram_base_addr["stack"]

        asmcode_list.append("// INIT SP" )       
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=A")   
        asmcode_list.append("@SP")        
        asmcode_list.append("M=D")
        asmcode_list.append("" )               

        return 
    
    def add_asmcode_push_stack(self, asmcode_list):
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("M=D")
        
        self.sp  += 0x1
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=A")   
        asmcode_list.append("@SP")        
        asmcode_list.append("M=D")
        return 
    
    def add_asmcode_pop_stack(self, asmcode_list):
        self.sp  -= 0x1
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=A")   
        asmcode_list.append("@SP")        
        asmcode_list.append("M=D")
        
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=M")                
        return 

    def add_asmcode_arithmetic(self, asmcode_list, arithmetic):
        self.sp  -= 0x1
        asmcode_list.append("@" + str(self.sp))
        if arithmetic in ["+", "-", "&", "|"]:
            asmcode_list.append("D=D" + arithmetic + "M")

        return 
    
    def setFileName(self, FileName):
        asmcode_list = []
        self.add_asmcode_init_sp(asmcode_list)
        self.fp.write('\n'.join(asmcode_list))
        self.fp.write('\n')        
        
        return

    def writeArithmetic(self, command):
        asmcode_list = []
              
        if command == "add":
            arithmetic = "+"
            self.add_asmcode_pop_stack(asmcode_list)
            self.add_asmcode_arithmetic(asmcode_list, arithmetic)
            self.add_asmcode_push_stack(asmcode_list)

        elif command == "sub":
            arithmetic = "-"
            self.add_asmcode_pop_stack(asmcode_list)
            self.add_asmcode_arithmetic(asmcode_list, arithmetic)
            self.add_asmcode_push_stack(asmcode_list)
            
        # elif command == "neg":
        #     arg1 = self.constant.pop()
        #     asmcode = "-" + arg1
        # elif command == "eq":
        #     asmcode = arg1 + "-" + arg2
        # elif command == "gt":
        #     asmcode = arg1 + "-" + arg2
        # elif command == "lt":
        #     asmcode = arg1 + "-" + arg2
        elif command == "and":
            arithmetic = "&"
            self.add_asmcode_pop_stack(asmcode_list)
            self.add_asmcode_arithmetic(asmcode_list, arithmetic)
            self.add_asmcode_push_stack(asmcode_list)
        elif command == "or":
            arithmetic = "|"
            self.add_asmcode_pop_stack(asmcode_list)
            self.add_asmcode_arithmetic(asmcode_list, arithmetic)
            self.add_asmcode_push_stack(asmcode_list)

        # elif command == "not":
        #     asmcode = arg1 + "-" + arg2

        print(" => ", asmcode_list)
        self.fp.write('\n'.join(asmcode_list))
        self.fp.write('\n')        
        
        return
    
    def writePushPop(self, command, segment, index):
        asmcode_list = []
        
        if command == "push":
            if segment == "constant":
                asmcode_list.append("@" + str(index))
                asmcode_list.append("D=A")
                self.add_asmcode_push_stack(asmcode_list)                
            
        elif command == "pop":
            if segment == "constant":
                self.add_asmcode_pop_stack(asmcode_list)
                asmcode_list.append("@" + str(index))  
                asmcode_list.append("M=D")

        print(" => ", asmcode_list)
        self.fp.write('\n'.join(asmcode_list))
        self.fp.write('\n')
        return

    def close(self):
        self.fp.close()
        return

'''
class RAM:

    def local(self, idx):
        # return LCL value + idx
        return LCL + idx

    def argument(self, idx):
        # return ARG value + idx        
        return ARG + idx

    def this(self, idx):
        # return THIS value + idx 
        return THIS + idx

    def that(self, idx):
        # return THAT value + idx         
        return THAT + idx

    def pointer(self, idx):
        # pointer refer THIS or THAT, so return only 3+i<=4
        return THIS + idx

    def temp(self, idx):
        # temp is 5~12, so return 5+i<=12
        return temp + idx
    
    def constant(self, idx):
        # return RAM_base + idx
        return idx

    def static(self, idx):
        # return static_base + idx
        return static + idx
'''
    
