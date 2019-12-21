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
        self.ram = [0] * 0x7fff
        
        # register
        self.sp = self.ram_base_addr["stack"]
        
        self.asmcode_list = []
        return 

    def setFileName(self, FileName):
        return

    def writeArithmetic(self, command):
        asmcode_list = []
        
        if command == "add":
            self.sp -= 0x1                        
            asmcode_list.append("@" + str(self.sp)) 
            asmcode_list.append("D=M")

            self.sp -= 0x1            
            asmcode_list.append("@" + str(self.sp)) 
            asmcode_list.append("D=D+M")
            
            asmcode_list.append("@" + str(self.sp)) 
            asmcode_list.append("M=D")
            self.sp += 0x1

        # elif command == "sub":
        # elif command == "neg":
        #     arg1 = self.constant.pop()
        #     asmcode = "-" + arg1
        # elif command == "eq":
        #     asmcode = arg1 + "-" + arg2
        # elif command == "gt":
        #     asmcode = arg1 + "-" + arg2
        # elif command == "lt":
        #     asmcode = arg1 + "-" + arg2
        # elif command == "and":
        #     asmcode = arg1 + "-" + arg2
        # elif command == "or":
        #     asmcode = arg1 + "-" + arg2
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
                asmcode_list.append("@" + str(self.sp))
                asmcode_list.append("M=D")
                
            self.sp += 0x1
            
        elif command == "pop":
            self.sp -= 0x1
            
            if segment == "constant":
                asmcode_list.append("@" + addr)                
                asmcode_list.append("D=M")
                asmcode_list.append("@" + self.sp)                
                asmcode_list.append("D=A")

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
    
