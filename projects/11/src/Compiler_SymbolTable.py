import os
import sys
import pprint

class SymbolTable:

    # type = {
    #     "var", "argument", "static", "field", "class", "subroutine"
    # }
    
    def __init__(self):
        self.SymbolTable = []
        self.var_idx        = 0
        self.argument_idx   = 0
        self.static_idx     = 0
        self.field_idx      = 0
        self.class_idx      = 0
        self.subroutine_idx = 0        
        return
    
    def startSubroutine(self):
        self.SymbolTable.clear()
        self.var_idx        = 0
        self.argument_idx   = 0
        self.static_idx     = 0
        self.field_idx      = 0
        
        return 

    def define(self, name , dtype, kind):
        kind_idx = 0

        if kind == "static":
            kind_idx = self.static_idx
            self.static_idx+=1
        elif kind == "field":
            kind_idx = self.field_idx
            self.field_idx+=1
        elif kind == "argument":
            kind_idx = self.argument_idx
            self.argument_idx+=1
        elif kind == "var":
            kind_idx = self.var_idx
            self.var_idx+=1
        else:
            print(name , " is invalid kind", kind, "! so ignored.")
            return
        
        new = [name, dtype, kind, kind_idx]
        self.SymbolTable.append(new)
        
        return 

    def varCount(self, kind):
        kind_idx = 0
        if kind == "static":
            kind_idx = self.static_idx
        elif kind == "field":
            kind_idx = self.field_idx
        elif kind == "argument":
            kind_idx = self.argument_idx
        elif kind == "var":
            kind_idx = self.var_idx
        else:
            print(kind , " is invalid kind!")
            return 0

        return kind_idx

    def kindOf(self, name):
        kind = "none"
        for i in range(len(self.SymbolTable)):
            defined = self.SymbolTable[i]
            defined_name = defined[0]
            if name == defined_name:
                kind = defined[2]
        
        return kind

    def typeOf(self, name):
        dtype = ""
        for i in range(len(self.SymbolTable)):
            defined = self.SymbolTable[i]
            defined_name = defined[0]
            if name == defined_name:
                dtype = defined[1]
                
        return dtype

    def indexOf(self, name):
        index = 0
        for i in range(len(self.SymbolTable)):
            defined = self.SymbolTable[i]
            defined_name = defined[0]
            if name == defined_name:
                index = defined[3]
                
        return index
    
