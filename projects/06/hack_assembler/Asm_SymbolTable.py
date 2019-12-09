import os
import sys

class SymbolTable:
    
    def __init__(self):
        self.symbol_table = []

    def addEntry(self, symbol, address):
        self.symbol_table.extend([symbol, address])
        return

    def contains(self, symbol):
        ret = False
        return ret

    def getAddress(self, symbol):
        ret = 0x0;
        return ret
        
    


        
