import os
import sys
import pprint

class SymbolTable:
    # type = {"var", "argument", "static", "field", "class", "subroutine", "none"}
    
    def __init__(self):
        self.SymbolTable = []
        # each subroutine has var, argument 
        self.var_idx        = 0
        self.argument_idx   = 0
        # each class has static, field
        self.static_idx     = 0
        self.field_idx      = 0
        # self.class_idx      = 0
        # self.subroutine_idx = 0        
        return
    
    def startSubroutine(self):
        # self.SymbolTable.clear()
        self.var_idx        = 0
        self.argument_idx   = 0
        # self.static_idx     = 0
        # self.field_idx      = 0
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
            # print(name , " is invalid kind", kind, "! so ignored.")
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
            return 0

        return kind_idx

    def isdefined(self, name):
        idx = -1
        for i in range(len(self.SymbolTable)):
            symbol      = self.SymbolTable[i]
            symbol_name = symbol[0]
            if name == symbol_name:
                idx = i
                
        return idx
    
    def kindOf(self, name):
        kind = "none"
        symbol_idx = self.isdefined(name)
        if symbol_idx >= 0:
            symbol = self.SymbolTable[symbol_idx]
            kind   = symbol[2]
        
        return kind

    def typeOf(self, name):
        dtype = ""
        symbol_idx = self.isdefined(name)
        if symbol_idx >= 0:
            symbol = self.SymbolTable[symbol_idx]
            dtype  = symbol[1]
                
        return dtype

    def indexOf(self, name):
        index = 0
        symbol_idx = self.isdefined(name)        
        if symbol_idx >= 0:
            symbol = self.SymbolTable[symbol_idx]
            index  = symbol[3]
                
        return index
    
