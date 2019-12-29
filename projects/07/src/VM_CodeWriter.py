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

    Register_for_Segment = {
         "constant" : "SP",     # Stack Pointer
         "local"    : "LCL",    # BaseAddr of local segment
         "argument" : "ARG",    # BaseAddr of argument segment
         "this"     : "THIS",   # BaseAddr of this segment in heap
         "that"     : "THAT",   # BaseAddr of that segment in heap
         "pointer"  : "3",      # 3 + index
         "temp"     : "5",      # 0x5~0xc for store temp segment value, 5 + index
         "general"  : "general" # 0xd~0xf can use as general register
    }
        
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

    def setReg(self, reg, val):
        '''
        set "val" to Register "reg"
        '''
        self.writeAsmCode2File("@" + str(val))
        self.writeAsmCode2File("D=A")        
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("M=D")
        return
        
    def setVal2RegrefAddr(self, reg, val):
        '''
        set "val" to RAM["reg"]
        '''
        self.writeAsmCode2File("@" + str(val))  
        self.writeAsmCode2File("D=A")
        self.setD2RegrefAddr(reg)
        return

    def setD2Addr(self, addr):
        '''
        set "Regiter D value" to RAM[addr]
        '''
        self.writeAsmCode2File("@" + addr)
        self.writeAsmCode2File("M=D")
        return
    
    def getAddr2D(self, addr):
        '''
        get RAM[addr] and set to "Regiter D value"
        '''
        self.writeAsmCode2File("@" + addr)
        self.writeAsmCode2File("D=M")
        return
    
    def setD2RegrefAddr(self, reg, idx=""):
        '''
        set "Regiter D value" to RAM["reg"+idx]
        '''
        if idx != "":
            # Once Store Register D value to R13
            self.writeAsmCode2File("@R13")
            self.writeAsmCode2File("M=D")  
            #calculate segment_base_addr + idx and store to R14
            self.writeAsmCode2File("@" + idx)
            self.writeAsmCode2File("D=A")
            self.writeAsmCode2File("@" + reg)
            self.writeAsmCode2File("D=D+M")
            self.writeAsmCode2File("@R14")
            self.writeAsmCode2File("M=D")  
            # set R13 value to segment_base_addr + idx
            self.writeAsmCode2File("@R13")
            self.writeAsmCode2File("D=M")
            self.writeAsmCode2File("@R14")
            self.writeAsmCode2File("A=M")
            self.writeAsmCode2File("M=D")                        
        else:
            self.writeAsmCode2File("@" + reg)
            self.writeAsmCode2File("A=M")
            self.writeAsmCode2File("M=D")            
        return
    
    def getRegrefAddrVal2D(self, reg, idx=""):
        '''
        get RAM["reg"+idx] value and set it to "Register D"
        '''
        if idx != "":
            #calculate segment_base_addr + idx
            self.writeAsmCode2File("@" + idx)
            self.writeAsmCode2File("D=A")
            self.writeAsmCode2File("@" + reg)
            self.writeAsmCode2File("D=D+M")
            # Once Store Register D value to R13
            self.writeAsmCode2File("@R13")
            self.writeAsmCode2File("M=D")  
            # get segment_base_addr + idx value to Register D
            self.writeAsmCode2File("@R13")
            self.writeAsmCode2File("A=M")
            self.writeAsmCode2File("D=M")  
        else:
            self.writeAsmCode2File("@" + reg)
            self.writeAsmCode2File("A=M")        
            self.writeAsmCode2File("D=M")            
        return

    def getArithmeticResult2D(self, reg, asmcode_arithmetic):
        '''
        get RAM["reg"] value, and calculate it, and store the result to Register D
        '''
        self.writeAsmCode2File("@" + reg)
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File(asmcode_arithmetic)        
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
        asmcode = self.AsmCodeArithmetic.get("sub", "")                
        self.comparison_label_cnt += 1
        # pop arg1
        self.decrementReg("SP")
        self.getRegrefAddrVal2D("SP")
        # pop arg2 and execute comparison
        self.decrementReg("SP")
        self.getArithmeticResult2D("SP", asmcode)
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

    def pushVal2Segment(self, reg, index):
        '''
        set "index" to RAM["reg"], and up reg
        '''
        if reg == "SP":
            self.setVal2RegrefAddr(reg, index)
            self.incrementReg("SP")  
        elif reg in ["LCL", "ARG", "THIS", "THAT"]:
            self.getRegrefAddrVal2D(reg, index)
            self.setD2RegrefAddr("SP")
            self.incrementReg("SP")
        else: # pointer, temp
            addr = int(index)
            if reg.isdigit:
                addr += int(reg)
            self.getAddr2D(str(addr))
            self.setD2RegrefAddr("SP")
            self.incrementReg("SP")
        return
    
    def popValfromSegment(self, reg, index):
        '''
        set "index" to RAM["reg"], and down reg
        '''
        if reg == "SP":
            self.setVal2RegrefAddr(reg, index)
            self.decrementReg("SP")                        
        elif reg in ["LCL", "ARG", "THIS", "THAT"]:
            self.decrementReg("SP")
            self.getRegrefAddrVal2D("SP")
            self.setD2RegrefAddr(reg, index)
        else: # pointer, temp
            addr = int(index)
            if reg.isdigit:
                addr += int(reg)
            self.decrementReg("SP")
            self.getRegrefAddrVal2D("SP")
            self.setD2Addr(str(addr))                
        return 

    def setFileName(self, FileName):
        # initialize SP value
        self.setReg("SP", self.ram_base_addr["stack"])
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
        register = self.Register_for_Segment.get(segment, "")
        if register != "":
            if command == "push":
                self.pushVal2Segment(register, index)              
            elif command == "pop":
                self.popValfromSegment(register, index)  
        return

    def close(self):
        self.fp.close()
        return
