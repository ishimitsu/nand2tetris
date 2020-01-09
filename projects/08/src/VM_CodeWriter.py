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
         "constant" : "SP",      # Stack Pointer
         "local"    : "LCL",     # BaseAddr of local segment
         "argument" : "ARG",     # BaseAddr of argument segment
         "this"     : "THIS",    # BaseAddr of this segment in heap
         "that"     : "THAT",    # BaseAddr of that segment in heap
         "pointer"  : "3",       # 3 + index
         "temp"     : "5",       # 0x5~0xc for store temp segment value, 5 + index
         "general"  : "general", # 0xd~0xf can use as general register
         "static"   : "static"      # segment for static starts from RAM[16]
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
        self.fname = ""
        self.comparison_label_cnt = 0
        self.return_address_label_cnt = 0        
        return 

    def writeAsmCode2File(self, asmcode):
        self.fp.write(asmcode + '\n')
        return

    def writeDebugAsmCode2File(self, asmcode):
        if not __debug__:
            self.writeAsmCode2File(asmcode)            
        return
    
    def incrementSP(self):
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("M=M+1")        
        return 

    def decrementSP(self):
        self.writeAsmCode2File("@SP")
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
        self.decrementSP()
        self.getRegrefAddrVal2D("SP")
        # pop arg2 and execute calculation
        self.decrementSP()
        self.getArithmeticResult2D("SP", asmcode_arithmetic)
        # store result
        self.setD2RegrefAddr("SP")
        self.incrementSP() 
        return 

    def Comparison(self, asmcode_comparison):
        label_idx   = str(self.comparison_label_cnt)
        label_true  = "TRUE_"  + label_idx
        label_false = "FALSE_" + label_idx
        label_exit  = "EXIT_"  + label_idx
        asmcode = self.AsmCodeArithmetic.get("sub", "")                
        self.comparison_label_cnt += 1
        # pop arg1
        self.decrementSP()
        self.getRegrefAddrVal2D("SP")
        # pop arg2 and execute comparison
        self.decrementSP()
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
        self.incrementSP()
        return 

    def NegOrNot(self, asmcode_arithmetic):
        # pop arg1
        self.decrementSP()
        self.getRegrefAddrVal2D("SP")        
        # neg or not
        self.writeAsmCode2File(asmcode_arithmetic)        
        self.writeAsmCode2File("M=D")

        self.incrementSP()
        return 

    def pushVal2Segment(self, reg, index):
        '''
        set "index" to RAM["reg"], and up reg
        '''
        if reg == "SP":
            self.setVal2RegrefAddr(reg, index)
            self.incrementSP()  
        elif reg in ["LCL", "ARG", "THIS", "THAT"]:
            self.getRegrefAddrVal2D(reg, index)
            self.setD2RegrefAddr("SP")
            self.incrementSP()
        elif reg == "static":
            self.getAddr2D(self.fname + "." + index)
            self.setD2RegrefAddr("SP")
            self.incrementSP()            
        elif reg.isdigit(): # pointer, temp            
            addr = int(reg) + int(index)
            self.getAddr2D(str(addr))
            self.setD2RegrefAddr("SP")
            self.incrementSP()
        return
    
    def popValfromSegment(self, reg, index):
        '''
        set "index" to RAM["reg"], and down reg
        '''
        if reg == "SP":
            self.setVal2RegrefAddr(reg, index)
            self.decrementSP()                        
        elif reg in ["LCL", "ARG", "THIS", "THAT"]:
            self.decrementSP()
            self.getRegrefAddrVal2D("SP")
            self.setD2RegrefAddr(reg, index)
        elif reg == "static":
            self.decrementSP()
            self.getRegrefAddrVal2D("SP")
            self.setD2Addr(self.fname + "." + index)
        elif reg.isdigit(): # pointer, temp
            addr = int(reg) + int(index)            
            self.decrementSP()
            self.getRegrefAddrVal2D("SP")
            self.setD2Addr(str(addr))
        return 

    def setFileName(self, FileName):
        self.fname = os.path.basename(FileName).split('.', 1)[0]
        return

    def writeInit(self):
        '''
        Initialize VM code (Boot Strap)
        '''
        # initialize SP=256
        self.writeDebugAsmCode2File("// Initialize VM code")
        self.writeAsmCode2File("@256")
        self.writeAsmCode2File("D=A")        
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("M=D")

        # call first-VM-func "Sys.init"
        self.writeCall("Sys.init")
        return

    def writeLabel(self, label):
        '''
        write asmcode for label command
        '''
        head = label[0]
        if head.isdigit():
            print("Invalid label name ", label)
            return
        
        self.writeAsmCode2File("(" + label + ")")
        return

    def writeGoto(self, label):
        '''
        write asmcode for goto command
        '''
        self.writeDebugAsmCode2File("//goto " + label)        
        self.writeAsmCode2File("@" + label) 
        self.writeAsmCode2File("0;JMP")  
        return

    def writeIf(self, label):
        '''
        write asmcode for if-goto command
        '''
        self.writeDebugAsmCode2File("//if-goto " + label) 
        # pop result of True or False, and store RegD
        self.decrementSP()
        self.getRegrefAddrVal2D("SP")
        self.writeAsmCode2File("@" + label)
        # jump label if D!=0(false)
        self.writeAsmCode2File("D;JNE")
        return

    def writeFunction(self, functionName, numLocals="0"):
        '''
        write asmcode for function command
        '''
        self.writeDebugAsmCode2File("// function " + functionName + " " + numLocals)         
        head = functionName[0]
        if head.isdigit():
            print("Invalid functionName ", functionName)
            return
        
        self.writeAsmCode2File("(" + functionName + ")")
        # local[numLocals] clear 0, and also push those vals to stack
        for i in range(int(numLocals)):
            # self.pushVal2Segment("LCL", str(i))
            self.writeAsmCode2File("@LCL")
            self.writeAsmCode2File("D=M")        
            self.writeAsmCode2File("@" + str(i))
            self.writeAsmCode2File("D=D+A")
            self.writeAsmCode2File("@R13")
            self.writeAsmCode2File("M=D")
            self.writeAsmCode2File("@0")
            self.writeAsmCode2File("D=A") 
            self.writeAsmCode2File("@R13")
            self.writeAsmCode2File("A=M")            
            self.writeAsmCode2File("M=D")             
            self.incrementSP()
            
        return
    
    def writeReturn(self):
        '''
        write asmcode for return command
        '''
        self.writeDebugAsmCode2File("// return") 
        # FRAME(R13) = LCL
        self.writeAsmCode2File("@LCL")
        self.writeAsmCode2File("D=M")        
        self.writeAsmCode2File("@R13")
        self.writeAsmCode2File("M=D")
        # Get RET(R14) = *(FRAME-5)
        self.writeAsmCode2File("@R13")
        self.writeAsmCode2File("D=M")  
        self.writeAsmCode2File("@5")        
        self.writeAsmCode2File("D=D-A")
        self.writeAsmCode2File("A=D")
        self.writeAsmCode2File("D=M")         
        self.writeAsmCode2File("@R14")
        self.writeAsmCode2File("M=D")        
        # *ARG = pop(), push func-result from Stack to ARG
        self.decrementSP()
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File("D=M")
        self.writeAsmCode2File("@ARG")
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File("M=D")
        # SP=ARG+1
        self.writeAsmCode2File("@ARG")
        self.writeAsmCode2File("D=M")    
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("M=D+1")        
        # THAT = *(FRAME-1)
        self.writeAsmCode2File("@R13")
        self.writeAsmCode2File("D=M")  
        self.writeAsmCode2File("@1")  
        self.writeAsmCode2File("D=D-A")
        self.writeAsmCode2File("A=D")
        self.writeAsmCode2File("D=M")         
        self.writeAsmCode2File("@THAT")
        self.writeAsmCode2File("M=D")        
        # THIS = *(FRAME-2)
        self.writeAsmCode2File("@R13")
        self.writeAsmCode2File("D=M")  
        self.writeAsmCode2File("@2")  
        self.writeAsmCode2File("D=D-A")
        self.writeAsmCode2File("A=D")
        self.writeAsmCode2File("D=M")                 
        self.writeAsmCode2File("@THIS")
        self.writeAsmCode2File("M=D")        
        # ARG = *(FRAME-3)
        self.writeAsmCode2File("@R13")
        self.writeAsmCode2File("D=M")  
        self.writeAsmCode2File("@3")  
        self.writeAsmCode2File("D=D-A")
        self.writeAsmCode2File("A=D")
        self.writeAsmCode2File("D=M")                 
        self.writeAsmCode2File("@ARG")
        self.writeAsmCode2File("M=D")        
        # LCL = *(FRAME-4)
        self.writeAsmCode2File("@R13")
        self.writeAsmCode2File("D=M")  
        self.writeAsmCode2File("@4")  
        self.writeAsmCode2File("D=D-A")
        self.writeAsmCode2File("A=D")
        self.writeAsmCode2File("D=M")                 
        self.writeAsmCode2File("@LCL")
        self.writeAsmCode2File("M=D")        
        # goto RET
        self.writeAsmCode2File("@R14")
        self.writeAsmCode2File("A=M")
        self.writeAsmCode2File("0;JMP")
        
        return

    def writeCall(self, functionName, numArgs="0"):
        '''
        write asmcode for call command
        '''
        self.writeDebugAsmCode2File("// call " + functionName + " " + numArgs)  
        return_address_label = "return-address_" + str(self.return_address_label_cnt)
        self.return_address_label_cnt +=1
        # push return-address
        self.writeAsmCode2File("@" + return_address_label)
        self.writeAsmCode2File("D=A")
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")        
        self.writeAsmCode2File("M=D")
        self.incrementSP()        
        # push LCL, ARG, THIS, THAT
        self.writeAsmCode2File("@LCL")
        self.writeAsmCode2File("D=M")
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")        
        self.writeAsmCode2File("M=D")
        self.incrementSP()        
        self.writeAsmCode2File("@ARG")
        self.writeAsmCode2File("D=M")
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")        
        self.writeAsmCode2File("M=D")
        self.incrementSP()        
        self.writeAsmCode2File("@THIS")
        self.writeAsmCode2File("D=M")
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")        
        self.writeAsmCode2File("M=D")
        self.incrementSP()        
        self.writeAsmCode2File("@THAT")
        self.writeAsmCode2File("D=M")
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("A=M")        
        self.writeAsmCode2File("M=D")
        self.incrementSP()        
        # ARG = SP-numArgs-5
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("D=M")
        self.writeAsmCode2File("@" + numArgs)
        self.writeAsmCode2File("D=D-A")
        self.writeAsmCode2File("@5")
        self.writeAsmCode2File("D=D-A")
        self.writeAsmCode2File("@ARG")
        self.writeAsmCode2File("M=D") 
        # LCL = SP
        self.writeAsmCode2File("@SP")
        self.writeAsmCode2File("D=M")
        self.writeAsmCode2File("@LCL")
        self.writeAsmCode2File("M=D")         
        # goto functionName
        self.writeAsmCode2File("@" + functionName)
        self.writeAsmCode2File("0;JMP")        
        # label (return-address)
        self.writeAsmCode2File("(" + return_address_label + ")")
        return
    
    def writeArithmetic(self, command):
        self.writeDebugAsmCode2File("// " + command)          
        asmcode = self.AsmCodeArithmetic.get(command, "")
        if command in ["add", "sub", "and", "or"]:
            self.Arithmetic(asmcode)  
        elif command in ["eq", "gt", "lt"]:
            self.Comparison(asmcode) 
        elif command in ["neg", "not"]:
            self.NegOrNot(asmcode)
        return
    
    def writePushPop(self, command, segment, index):
        self.writeDebugAsmCode2File("// " + command + " " + segment + " " + index)         
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

