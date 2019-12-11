import os
import sys

class Parser:
    def __init__(self, asm_file):
        self.cur_line   = 0
        self.cur_cmd    = ""
        self.cmd_type   = "NOT_COMMAND"
        self.a_symbol = ""
        self.c_dest = self.c_comp = self.c_jump = ""
        
        if os.path.isfile(asm_file):
            fp = open(asm_file)
            self.readlines = fp.readlines()
            self.lines = len(self.readlines)
            fp.close()
        
    def hasMoreCommands(self):
        ret = False
        if self.cur_line < self.lines:
            ret = True
        return ret

    def advance(self):
        self.cur_cmd = self.readlines[self.cur_line]
        self.cur_line+=1
        return

    def commandType(self):
        self.cmd_type = "NOT_COMMAND"
        self.a_symbol = ""
        self.c_dest = self.c_comp = self.c_jump = ""
        
        cmd = self.cur_cmd.split()
        if( len(cmd) == 0):
            self.cmd_type = "NOT_COMMAND"            
            return "NOT_COMMAND"

        cmd_head = cmd[0]
        if   cmd_head.startswith('//'):
            self.cmd_type = "NOT_COMMAND"
        elif cmd_head.startswith('@'):
            self.cmd_type = "A_COMMAND"
            self.a_symbol   = cmd_head.strip('@')
        elif cmd_head.startswith('('):
            self.cmd_type = "L_COMMAND"
            self.a_symbol   = cmd_head.strip('()')
        elif '=' in cmd_head:
            self.cmd_type = "C_COMMAND"
            comp_dest = cmd_head.split('=')
            self.c_dest = comp_dest[0]
            self.c_comp = comp_dest[1]            
        elif ';' in cmd_head:
            self.cmd_type = "C_COMMAND"        
            comp_jump = cmd_head.split(';')
            self.c_comp = comp_jump[0]
            self.c_jump = comp_jump[1]            
        else :
            self.cmd_type = "NOT_COMMAND"

        return self.cmd_type

    def symbol(self):
        return self.a_symbol

    def dest(self):
        return self.c_dest

    def comp(self):
        return self.c_comp
    
    def jump(self):
        return self.c_jump
        

        
