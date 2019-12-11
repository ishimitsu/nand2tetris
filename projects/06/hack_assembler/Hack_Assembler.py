import os
import sys

from Asm_Parser import Parser 
from Asm_Code import Code
from Asm_SymbolTable import SymbolTable

def test_Parser(parser):
    ret = True

    while parser.hasMoreCommands():
        parser.advance()
        cmd_type = parser.commandType()

        if cmd_type == "A_COMMAND" or cmd_type == "L_COMMAND":
            symbol = parser.symbol()            
            print("TYPE:", cmd_type, "\t Symbol:", symbol)            
        elif cmd_type == "C_COMMAND":
            dest = parser.dest()
            comp = parser.comp()
            jump = parser.jump()            
            print("TYPE:", cmd_type, "\t dest:", dest, "\t comp:", comp, "\t jump:", jump)
            
    return ret

if __name__ == '__main__':

    args = sys.argv
    if len(args) == 2:
        parser = Parser(args[1])
        symbol_table = SymbolTable();

        test_Parser(parser)
                
    else:
        print("Invalid Args!");
        
    sys.exit()
