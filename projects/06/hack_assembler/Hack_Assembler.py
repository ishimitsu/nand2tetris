import os
import sys
import pprint

from Asm_Parser import Parser 
from Asm_Code import Code
from Asm_SymbolTable import SymbolTable

class HackAssember:

    variable_symbol_table_start_addr = 0x0010
    def __init__(self):
        self.var_symbol_table_end_addr = self.variable_symbol_table_start_addr
    
    def add_new_symbol2table(self, symbol, symbol_table):
        symbol_addr = self.var_symbol_table_end_addr
        symbol_table.addEntry(symbol, symbol_addr)
        self.var_symbol_table_end_addr += 0x1
        return symbol_addr
    
    def get_a_cmd_bincode (self,  parser, code, symbol_table):
        symbol      = parser.symbol()
        symbol_addr = 0x0

        if symbol.isdigit():
            symbol_addr = int(symbol)
        else:
            if symbol_table.contains(symbol):
                symbol_addr = symbol_table.getAddress(symbol)
            else:
                symbol_addr = self.add_new_symbol2table(symbol, symbol_table)

        bincode = format(symbol_addr, '016b')            
        return bincode

    def get_c_cmd_bincode (self, parser, code):
        c_dest = parser.dest()
        c_comp = parser.comp()
        c_jump = parser.jump()

        c_cmd_code = 0b111 #3bit
        comp_code  = 0b0   #7it
        dest_code  = 0b000 #3bit
        jump_code  = 0b000 #3bit
    
        if   len(c_dest) > 0:
            comp_code  = code.comp(c_comp)
            dest_code  = code.dest(c_dest)                
            jump_code  = 0b000
        elif len(c_jump) > 0:
            comp_code = code.comp(c_comp)
            dest_code = 0b000                
            jump_code = code.jump(c_jump)

        bincode = bin(c_cmd_code<<13 | comp_code<<6 | dest_code<<3 | jump_code)[2:]
        return bincode


    def cvt_a_c_cmd2bincode(self, asm_file, symbol_table):
        parser = Parser(asm_file)
        code   = Code()
        bincode_list = []
        while parser.hasMoreCommands():
            parser.advance()
            cmd_type = parser.commandType()
            if cmd_type == "A_COMMAND":
                bincode = self.get_a_cmd_bincode(parser, code, symbol_table)
                bincode_list.append(bincode)
            elif cmd_type == "C_COMMAND":
                bincode = self.get_c_cmd_bincode(parser, code)
                bincode_list.append(bincode)
        return bincode_list

    
    def find_l_cmd_symbol2table(self, asm_file, symbol_table):
        parser = Parser(asm_file)
        rom_addr = 0x0
        while parser.hasMoreCommands():
            parser.advance()
            cmd_type = parser.commandType()
            if cmd_type == "L_COMMAND":
                symbol = parser.symbol()                
                symbol_table.addEntry(symbol, rom_addr)
            elif cmd_type in {"A_COMMAND", "C_COMMAND"}:
                rom_addr += 0x1
        return
    
    
    def convert_asm2bincode(self, asm_file, hack_file):
        symbol_table = SymbolTable();

        self.find_l_cmd_symbol2table(asm_file, symbol_table)
        bincode_list = self.cvt_a_c_cmd2bincode(asm_file, symbol_table)
        # pprint.pprint(symbol_table.symbol_table)        
        # pprint.pprint(bincode_list)        
        
        with open(hack_file, mode='w') as fp_hack:
            fp_hack.writelines('\n'.join(bincode_list))
            fp_hack.write('\n')

        return

if __name__ == '__main__':

    args = sys.argv
    if len(args) == 2:
        asm_file   = args[1]
        hack_file  = os.path.split(asm_file)[0] + '/' + os.path.basename(asm_file).split('.', 1)[0] + ".hack"
        hack_assembler = HackAssember()        
        parsed_cmd     = hack_assembler.convert_asm2bincode(asm_file, hack_file)
    else:
        print("Invalid Args!");
        
    sys.exit()
