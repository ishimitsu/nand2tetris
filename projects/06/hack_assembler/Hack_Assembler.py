import os
import sys

from Asm_Parser import Parser 
from Asm_Code import Code
from Asm_SymbolTable import SymbolTable

def get_c_cmd_bincode (parser, code):
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
    print("TYPE:", parser.commandType(), " => BINCODE:", bincode)                    
    return bincode


def convert_asm_to_bincode(asm_file, hack_file):
    parser = Parser(asm_file)
    code   = Code()
    symbol_table = SymbolTable();
    bincode_list = []
    
    while parser.hasMoreCommands():
        parser.advance()
        cmd_type = parser.commandType()
        bincode = 0b0   #16bit
        # print(parser.cur_cmd, end="=> ")  
        
        if cmd_type in {"A_COMMAND", "L_COMMAND"}:
            a_symbol = parser.symbol()
            if a_symbol.isdigit():
                a_value = int(a_symbol)
                bincode = format(a_value, '016b')
                
            bincode_list.append(bincode)
            print("TYPE:", cmd_type, " => BINCODE:", bincode) 

        elif cmd_type == "C_COMMAND":
            bincode = get_c_cmd_bincode(parser, code)
            bincode_list.append(bincode)

    with open(hack_file, mode='w') as fp_hack:
        fp_hack.writelines('\n'.join(bincode_list))
        fp_hack.write('\n')
            
    return

if __name__ == '__main__':

    args = sys.argv
    if len(args) == 2:
        asm_file   = args[1]
        hack_file  = os.path.split(asm_file)[0] + '/' + os.path.basename(asm_file).split('.', 1)[0] + ".hack"
        print(hack_file)
        parsed_cmd = convert_asm_to_bincode(asm_file, hack_file)
    else:
        print("Invalid Args!");
        
    sys.exit()
