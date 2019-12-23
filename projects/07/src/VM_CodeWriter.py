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
        self.comparison_cnt = 0
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
        asmcode_list.append("")
        
        asmcode_list.append("(TOP)")        
        
        return 
    
    def add_asmcode_push_stack(self, asmcode_list):
        asmcode_list.append("// PUSH STACK") # debug
        
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("M=D")
        
        self.sp  += 0x1
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=A")   
        asmcode_list.append("@SP")        
        asmcode_list.append("M=D")
        return 
    
    def add_asmcode_pop_stack(self, asmcode_list):
        asmcode_list.append("// POP STACK") # debug

        self.sp  -= 0x1
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=A")   
        asmcode_list.append("@SP")        
        asmcode_list.append("M=D")
        
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=M")
        return 

    def add_asmcode_arithmetic(self, asmcode_list, asmcode_arithmetic):
        asmcode_list.append("// ARITHMETIC: " + asmcode_arithmetic ) # debug

        self.sp  -= 0x1
        asmcode_list.append("@" + str(self.sp))  
        asmcode_list.append(asmcode_arithmetic)
        
        return 

    def add_asmcode_comparison(self, asmcode_list, asmcode_comparison):
        label_idx   = str(self.comparison_cnt)
        label_true  = "TRUE_"  + label_idx
        label_false = "FALSE_" + label_idx
        label_exit  = "EXIT_"  + label_idx
        self.comparison_cnt += 1

        asmcode_list.append("// COMPARISON:  " + asmcode_comparison ) # debug
        
        self.sp  -= 0x1        
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=M-D")
        asmcode_list.append("@" + label_true) 
        asmcode_list.append(asmcode_comparison)
        asmcode_list.append("@" + label_false) 
        asmcode_list.append("0;JMP")  

        # true case
        asmcode_list.append("(" + label_true + ")")
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("M=-1")
        asmcode_list.append("@" + label_exit)        
        asmcode_list.append("0;JMP")
        # false case
        asmcode_list.append("(" + label_false + ")")
        asmcode_list.append("@" + str(self.sp))        
        asmcode_list.append("M=0")
        # exit
        asmcode_list.append("(" + label_exit + ")")
        
        # move sp, because pushed M = -1 or 0      
        self.sp  += 0x1
        asmcode_list.append("@" + str(self.sp))
        asmcode_list.append("D=A")   
        asmcode_list.append("@SP")        
        asmcode_list.append("M=D")
        
        return 

    def add_asmcode_neg_not(self, asmcode_list, asmcode_arithmetic):
        asmcode_list.append("// NEG, NOT: " + asmcode_arithmetic ) # debug

        asmcode_list.append("@" + str(self.sp))  
        asmcode_list.append(asmcode_arithmetic)
        
        return 
    
    def setFileName(self, FileName):
        asmcode_list = []
        self.add_asmcode_init_sp(asmcode_list)
        self.fp.write('\n'.join(asmcode_list))
        self.fp.write('\n')        
        
        return

    def writeArithmetic(self, command):
        asmcode_list = []
        asmcode_arithmetic = ""
        
        if command in ["add", "sub", "and", "or"]:
            if command == "add":
                asmcode_arithmetic = "D=D+M"
            elif command == "sub":
                asmcode_arithmetic = "D=M-D"                
            elif command == "and":
                asmcode_arithmetic = "D=D&M"
            elif command == "or":
                asmcode_arithmetic = "D=D|M"
            self.add_asmcode_pop_stack(asmcode_list) # get arg1            
            self.add_asmcode_arithmetic(asmcode_list, asmcode_arithmetic)                
            self.add_asmcode_push_stack(asmcode_list) # push result

        elif command in ["eq", "gt", "lt"]:
            if command == "eq":
                asmcode_arithmetic = "D;JEQ" 
            elif command == "gt":
                asmcode_arithmetic = "D;JGT"                 
            elif command == "lt":
                asmcode_arithmetic = "D;JLT"                
            self.add_asmcode_pop_stack(asmcode_list) # get arg1            
            self.add_asmcode_comparison(asmcode_list, asmcode_arithmetic) 
            
        elif command in ["neg", "not"]:
            if command == "neg":
                asmcode_arithmetic = "D=-D"
            elif command == "not":
                asmcode_arithmetic = "D=!D"
            self.add_asmcode_pop_stack(asmcode_list) # get arg1                
            self.add_asmcode_neg_not(asmcode_list, asmcode_arithmetic)
            self.add_asmcode_push_stack(asmcode_list)
                
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
    
