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
    ArithmeticCMD = ['add', 'sub', 'and', 'or', 'not', 'eq', 'lt', 'gt', 'neg']

    def __init__(self, file):
        self.cur_line = self.lines = 0
        self.cur_cmd  = ""
        self.cmd_type = "NOT_COMMAND"
        self.args     = []
        
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
        elif cmd_head.startswith('push'):
            self.cmd_type = "C_PUSH"
        elif cmd_head.startswith('pop'):
            self.cmd_type = "C_POP"
        elif cmd_head.startswith('label'):
            self.cmd_type = "C_LABEL"
        elif cmd_head.startswith('goto'):
            self.cmd_type = "C_GOTO"
        elif cmd_head.startswith('if'):
            self.cmd_type = "C_IF"
        elif cmd_head.startswith('function'):
            self.cmd_type = "C_FUNCTION"
        elif cmd_head.startswith('return'):
            self.cmd_type = "C_RETURN"
        elif cmd_head.startswith('call'):
            self.cmd_type = "C_CALL"
        elif cmd_head in self.ArithmeticCMD:
            self.cmd_type = "C_ARITHMETIC"
        else :
            self.cmd_type = "NOT_COMMAND"

        if self.cmd_type != "NOT_COMMAND":
            self.args = cmd
            
        return self.cmd_type

    def arg1(self):
        ret = ""
        if self.cmd_type == "C_ARITHMETIC":
            ret = self.args[0]
        elif self.cmd_type in ["NOT_COMMAND", "C_RETURN"]:
            ret = ""            
        else :
            ret = self.args[1]              
        return ret

    def arg2(self):
        ret = ""        
        if self.cmd_type in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
            ret = self.args[2]
        return ret
