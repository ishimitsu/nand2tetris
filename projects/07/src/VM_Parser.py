import os
import sys
import pprint

class Parser:
    val_symbol_start_addr = 0x10
    AsmSymbol = {
        "SP"     : 0x0, "LCL"    : 0x1, "ARG"    : 0x2, "THIS"   : 0x3, "THAT"   : 0x4,
        "R0"     : 0x0, "R1"     : 0x1, "R2"     : 0x2, "R3"     : 0x3,
        "R4"     : 0x4, "R5"     : 0x5, "R6"     : 0x6, "R7"     : 0x7,
        "R8"     : 0x8, "R9"     : 0x9, "R10"    : 0xa, "R11"    : 0xb,
        "R12"    : 0xc, "R13"    : 0xd, "R14"    : 0xe, "R15"    : 0xf,              
        "SCREEN" : 0x4000, "KBD"    : 0x6000
    }

    def __init__(self, file):
        self.cur_line = self.lines = 0
        self.cur_cmd  = ""
        
        if os.path.isfile(file):
            fp = open(file)
            self.readlines = fp.readlines()
            self.lines = len(self.readlines)
            fp.close()
            
        return

    def hasMoreCommands(self):
        return self.cur_line < self.lines

    def advance(self):
        self.cur_cmd = self.readlines[self.cur_line]
        self.cur_line+=1
        return

    def commandType(self):
        self.cmd_type = "NOT_COMMAND"
        
        cmd = self.cur_cmd.split()
        if( len(cmd) == 0):
            self.cmd_type = "NOT_COMMAND"            
            return "NOT_COMMAND"

        cmd_head = cmd[0]
        if   cmd_head.startswith('//'):
            self.cmd_type = "NOT_COMMAND"
        elif 'push' in cmd_head:
            self.cmd_type = "C_PUSH"
        elif 'pop' in cmd_head:
            self.cmd_type = "C_POP"
        elif 'label' in cmd_head:
            self.cmd_type = "C_LABEL"            
        elif 'goto' in cmd_head:
            self.cmd_type = "C_GOTO"
        elif 'if' in cmd_head:
            self.cmd_type = "C_IF"            
        elif 'function' in cmd_head:
            self.cmd_type = "C_FUNCTION"            
        elif 'return' in cmd_head:
            self.cmd_type = "C_RETURN"
        elif 'call' in cmd_head:
            self.cmd_type = "C_CALL"   
        elif '+-&|=' in cmd_head:
            self.cmd_type = "C_ARITHMETIC"            
        else :
            self.cmd_type = "NOT_COMMAND"

        return self.cmd_type

    def arg1(self, args):
        arg1 = ""
        return arg1

    def arg2(self, args):
        arg2 = ""
        return arg2

'''
class RAM:
    # MemoryMap

    # 0~0xf for 16 registers
    register = {
        "SP"     : 0x0,  # Stack Pointer
        "LCL"    : 0x1,  # BaseAddr of local segment
        "ARG"    : 0x2,  # BaseAddr of argument segment
        "THIS"   : 0x3,  # BaseAddr of this segment in heap
        "THAT"   : 0x4,  # BaseAddr of that segment in heap
        "temp"   : 0x5,  # 0x5~0xc for store temp segment value
        "general" : 0xd  # 0xd~0xf can use as general register
    }

    # 0x10   ~ 0xff, for static
    # 0x100  ~ 0x7ff, for stack
    # 0x800  ~ 0x3fff, for heap
    # 0x4000 ~ 0x5fff, for MMIO
    # 0x6000 ~ 0x7fff, unused        

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
