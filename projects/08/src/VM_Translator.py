import os
import sys
import glob
import pprint

from VM_Parser import Parser
from VM_CodeWriter import CodeWriter

class VMtranslator:
    def __init__(self):
        return

    def open_file_or_dir(self, path):
        vm_file_list = []
        asm_file_list = []        
        
        if os.path.isfile(path):
            vm_file  = path
            asm_file = os.path.split(vm_file)[0] + '/' + os.path.basename(vm_file).split('.', 1)[0] + ".asm"
            vm_file_list.append(vm_file)
            asm_file_list.append(asm_file)                       
        elif os.path.isdir(path):
           vm_file_list = glob.glob(path + "/*.vm")
           for i in range(len(vm_file_list)):
               vm_file = vm_file_list[i]
               asm_file = os.path.split(vm_file)[0] + '/' + os.path.basename(vm_file).split('.', 1)[0] + ".asm"
               asm_file_list.append(asm_file)
               
        return vm_file_list, asm_file_list

    
    def vm_translator(self, vm_file, asm_file):
        parser      = Parser(vm_file)
        code_writer = CodeWriter(asm_file)        
        code_writer.setFileName(asm_file)
        code_writer.writeInit()        
        
        while parser.hasMoreCommands():
            parser.advance()
            cmd_type = parser.commandType()
            if cmd_type != "NOT_COMMAND":
                cmd  = parser.args[0]
                arg1 = parser.arg1()
                arg2 = parser.arg2()
                # print(parser.cur_cmd, " => ", parser.args)

                if parser.cmd_type == "C_ARITHMETIC":
                    code_writer.writeArithmetic(cmd)
                elif parser.cmd_type in ["C_PUSH", "C_POP"]:
                    code_writer.writePushPop(cmd, arg1, arg2)
                elif parser.cmd_type == "C_LABEL":
                    code_writer.writeLabel(arg1)
                elif parser.cmd_type == "C_GOTO":
                    code_writer.writeGoto(arg1)
                elif parser.cmd_type == "C_IF":
                    code_writer.writeIf(arg1)
                elif parser.cmd_type == "C_FUNCTION":
                    code_writer.writeFunction(arg1, arg2)
                elif parser.cmd_type == "C_RETURN":
                    code_writer.writeCall()
                elif parser.cmd_type == "C_CALL":
                    code_writer.writeCall(arg1, arg2)
                else:
                    print("Invalid Command, [", cmd, "]")
                    
        code_writer.close()
        return

if __name__ == '__main__':

    args = sys.argv
    if len(args) == 2:
        path = args[1]
        vt   = VMtranslator()
        vm_flist, asm_flist = vt.open_file_or_dir(path)
        print(vm_flist)
        print(asm_flist)

        for i in range(len(vm_flist)):
            vm_file  = vm_flist[i]
            asm_file = asm_flist[i]            
            vm2asm = vt.vm_translator(vm_file, asm_file)
    else:
        print("Invalid Args!");
        
    sys.exit()
