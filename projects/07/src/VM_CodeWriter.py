import os
import sys
import pprint
# import numpy as np

class CodeWriter:
    ram_base_addr = {
        "reg"    : 0x0,    # 0x0    ~ 0xf, for 16 registers
        "static" : 0x10,   # 0x10   ~ 0xff, for static
        "stack"  : 0x100,  # 0x100  ~ 0x7ff, for stack
        "heap"   : 0x800,  # 0x800  ~ 0x3fff, for heap
        "mmio"   : 0x4000, # 0x4000 ~ 0x5fff, for MMIO
        "unused" : 0x6000  # 0x6000 ~ 0x7fff, unused        
    }

    '''
        Register Name and Location on RAM
         "SP"     : 0x0,  # Stack Pointer
         "LCL"    : 0x1,  # BaseAddr of local segment
         "ARG"    : 0x2,  # BaseAddr of argument segment
         "THIS"   : 0x3,  # BaseAddr of this segment in heap
         "THAT"   : 0x4,  # BaseAddr of that segment in heap
         "temp"   : 0x5,  # 0x5~0xc for store temp segment value
         "general" : 0xd  # 0xd~0xf can use as general register
    '''
        
    AsmCodeArithmetic = {
        "add" : "D=D+M",
        "sub" : "D=M-D",
        "and" : "D=D&M",
        "or"  : "D=D|M",
        "eq"  : "D;JEQ",
        "gt"  : "D;JGT",
        "lt"  : "D;JLT",
        "neg" : "D=-D",
        "not" : "D=!D"        
    }
    
    def __init__(self, file):
        self.fp = open(file, mode='w')
        self.comparison_label_cnt = 0
        return 

    def writeAsmCode2File(self, asmcode):
        self.fp.write(asmcode + '\n')
        return

    def incrementReg(self, reg):
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("M=M+1")        
        return 

    def decrementReg(self, reg):
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("M=M-1")
        return 

    def setRegVal(self, reg, val):
        self.writeAsmCode2File("@" + str(val))
        self.writeAsmCode2File("D=A")        
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("M=D")
        return
    
    def setD2RegrefAddr(self, reg):
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File("M=D")
        return
    
    def setVal2RegrefAddr(self, reg, val):
        self.writeAsmCode2File("@" + str(val))  
        self.writeAsmCode2File("D=A")
        self.setD2RegrefAddr(reg)
        return

    def getRegrefAddrVal2D(self, reg):
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("A=M")        
        self.writeAsmCode2File("D=M")
        return

    def getArithmeticResult2D(self, reg, asmcode_arithmetic):
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File(asmcode_arithmetic)        
        return
    
    def pushVal2Stack(self, index):
        self.setVal2RegrefAddr("SP", index)
        self.incrementReg("SP")        
        return 
    
    def popValfromStack(self, index):
        self.setVal2RegrefAddr("SP", index)
        self.decrementReg("SP")
        return 
    
    def Arithmetic(self, asmcode_arithmetic):
        # pop arg1
        self.decrementReg("SP")
        self.getRegrefAddrVal2D("SP")
        # pop arg2 and execute calculation
        self.decrementReg("SP")
        self.getArithmeticResult2D("SP", asmcode_arithmetic)
        # store result
        self.setD2RegrefAddr("SP")
        self.incrementReg("SP")         
        return 

    def Comparison(self, asmcode_comparison):
        label_idx   = str(self.comparison_label_cnt)
        label_true  = "TRUE_"  + label_idx
        label_false = "FALSE_" + label_idx
        label_exit  = "EXIT_"  + label_idx
        self.comparison_label_cnt += 1
        # pop arg1
        self.decrementReg("SP")
        self.getRegrefAddrVal2D("SP")
        # pop arg2 and execute comparison
        self.decrementReg("SP")
        self.getArithmeticResult2D("SP", "D=M-D")
        self.writeAsmCode2File("@" + label_true) 
        self.writeAsmCode2File(asmcode_comparison)
        self.writeAsmCode2File("@" + label_false) 
        self.writeAsmCode2File("0;JMP")  
        # true case
        self.writeAsmCode2File("(" + label_true + ")")
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File("M=-1") # write true
        self.writeAsmCode2File("@" + label_exit)        
        self.writeAsmCode2File("0;JMP")
        # false case
        self.writeAsmCode2File("(" + label_false + ")")
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File("M=0")  # write false
        # exit
        self.writeAsmCode2File("(" + label_exit + ")")
        # move sp, because pushed M = -1 or 0
        self.incrementReg("SP")
        return 

    def NegOrNot(self, asmcode_arithmetic):
        # pop arg1
        self.decrementReg("SP")
        self.getRegrefAddrVal2D("SP")        
        # neg or not
        self.writeAsmCode2File(asmcode_arithmetic)        
        self.writeAsmCode2File("M=D")

        self.incrementReg("SP")
        return 
    
    def setFileName(self, FileName):
        self.setRegVal("SP", self.ram_base_addr["stack"])
        return

    def writeArithmetic(self, command):
        asmcode = self.AsmCodeArithmetic.get(command, "")
        if command in ["add", "sub", "and", "or"]:
            self.Arithmetic(asmcode)  
        elif command in ["eq", "gt", "lt"]:
            self.Comparison(asmcode) 
        elif command in ["neg", "not"]:
            self.NegOrNot(asmcode)
                
        return
    
    def writePushPop(self, command, segment, index):
        if command == "push":
            if segment == "constant":
                self.pushVal2Stack(index)                
            elif segment == "local":
                self.pushVal2Stack(index)                
            elif segment == "argument":
                self.pushVal2Stack(index)                
            elif segment == "this":
                self.pushVal2Stack(index)                
            elif segment == "that":
                self.pushVal2Stack(index)                
            elif segment == "temp":
                self.pushVal2Stack(index)
                
        elif command == "pop":
            if segment == "constant":
                self.popValfromStack(index)
            if segment == "local":
                self.popValfromStack(index)
            if segment == "argument":
                self.popValfromStack(index)
            if segment == "this":
                self.popValfromStack(index)
            if segment == "that":
                self.popValfromStack(index)
            if segment == "temp":
                self.popValfromStack(index)

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
    
