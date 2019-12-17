import os
import sys
import pprint

from VM_Parser import Parser
from VM_CodeWriter import CodeWriter

class VMtranslator:
    def __init__(self):
        return

    def vm_translator(self, vm_file, asm_file):
        parser = Parser(vm_file)
        pprint.print(parser.readlines)
        return

if __name__ == '__main__':

    args = sys.argv
    if len(args) == 2:
        vm_file   = args[1]
        asm_file  = os.path.split(vm_file)[0] + '/' + os.path.basename(vm_file).split('.', 1)[0] + ".asm"
        vt = VMtranslator()
        vm2asm = vt.vm_translator(vm_file, asm_file)
    else:
        print("Invalid Args!");
        
    sys.exit()
