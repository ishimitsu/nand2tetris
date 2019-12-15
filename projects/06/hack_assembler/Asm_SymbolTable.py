import os
import sys

class SymbolTable:

    val_symbol_start_addr = 0x0010
    symbol_table = {
        "SP"     : 0x0, "LCL"    : 0x1, "ARG"    : 0x2, "THIS"   : 0x3, "THAT"   : 0x4,
        "R0"     : 0x0, "R1"     : 0x1, "R2"     : 0x2, "R3"     : 0x3,
        "R4"     : 0x4, "R5"     : 0x5, "R6"     : 0x6, "R7"     : 0x7,
        "R8"     : 0x8, "R9"     : 0x9, "R10"    : 0xa, "R11"    : 0xb,
        "R12"    : 0xc, "R13"    : 0xd, "R14"    : 0xe, "R15"    : 0xf,              
        "SCREEN" : 0x4000, "KBD"    : 0x6000
    }
    
    def __init__(self):
        self.val_symbol_table = []

    def addEntry(self, symbol, address):
        # new = {symbol, address}
        # print("new l label", new)
        # self.symbol_table.update(new)
        self.symbol_table[symbol] = address
        return

    def contains(self, symbol):
        return symbol in self.symbol_table

    def getAddress(self, symbol):
        return self.symbol_table.get(symbol)
        
    


        
