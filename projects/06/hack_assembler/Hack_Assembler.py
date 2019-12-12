import os
import sys

from Asm_Parser import Parser 
from Asm_Code import Code
from Asm_SymbolTable import SymbolTable

def convert_asm_to_bincode(asm_file):
    parser = Parser(asm_file)
    code   = Code()
    symbol_table = SymbolTable();    
    
    while parser.hasMoreCommands():
        parser.advance()
        cmd_type = parser.commandType()

        if cmd_type in {"A_COMMAND", "L_COMMAND"}:
            print(parser.cur_cmd, end="=> ")  
            a_symbol = parser.symbol()            
            print("TYPE:", cmd_type, "\t Symbol:", a_symbol, end="\t\t=>\t")
            print("BINCODE:")            
        elif cmd_type == "C_COMMAND":
            print(parser.cur_cmd, end="=> ")              
            c_dest = parser.dest()
            c_comp = parser.comp()
            c_jump = parser.jump()

            c_cmd_code = 0b111 #3bit
            comp_code  = 0b0   #7it
            dest_code  = 0b000 #3bit
            jump_code  = 0b000 #3bit
            bin_code   = 0b0   #16bit
            if   len(c_dest) > 0:
                comp_code  = code.comp(c_comp)
                dest_code  = code.dest(c_dest)                
                jump_code  = 0b000
                print("TYPE:", cmd_type, "\t dest:", c_dest, "\t comp:", c_comp, end="\t=>\t")   
                
            elif len(c_jump) > 0:
                comp_code = code.comp(c_comp)
                dest_code = 0b000                
                jump_code = code.jump(c_jump)
                print("TYPE:", cmd_type, "\t comp:", c_comp, "\t jump:", c_jump, end="\t=>\t")

            bin_code = bin(c_cmd_code<<13 | comp_code<<6 | dest_code<<3 | jump_code)
            print("BINCODE:", bin_code)   
    return

if __name__ == '__main__':

    args = sys.argv
    if len(args) == 2:
        asm_file   = args[1]
        parsed_cmd = convert_asm_to_bincode(asm_file)
    else:
        print("Invalid Args!");
        
    sys.exit()
