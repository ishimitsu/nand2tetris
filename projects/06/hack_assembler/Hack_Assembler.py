import os
import sys

from Asm_Parser import Parser 
from Asm_Code import Code
from Asm_SymbolTable import SymbolTable

def asm_parser(asm_file):
    if os.path.isfile(asm_file):
        fp = open(asm_file)
        readline = fp.readlines()
        print("line ", len(readline))
        for i in range(0, len(readline)):
            print(readline[i])

        fp.close()

if __name__ == '__main__':

    args = sys.argv
    if len(args) == 2:
        parser = Parser(args[1])
        asm_parser(parser.asm_file);
    else:
        print("Invalid Args!");
        
    sys.exit()
