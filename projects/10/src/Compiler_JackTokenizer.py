import os
import sys
import glob
import pprint

class JackTokenizer:

    tokenType_keyword = ['class', 'constructor', 'function',
                         'method', 'field', 'static', 'var',
                         'int', 'char', 'boolean', 'void',
                         'true', 'false', 'null', 'this',
                         'let', 'do', 'if', 'else',
                         'while', 'return']                         
    tokenType_symbol = ['{', '}', '(', ')', '[', ']', '.', ',',
                        ';', '+', '-', '*', '/', '&',
                        '|', '<', '>', '=', '~']                         
     
    tokenType_keyword = {
        "keyword"      : "KEYWORD",
        "symbol"       : "SYMBOL",
        "identifier"   : "IDENTIFIER",
        "int_const"    : "INT_CONST",
        "string_const" : "STRING_CONST"
    }
    
    keyWord_dict = {
        "class"       : "CLASS",
        "method"      : "METHOD",
        "function"    : "FUNCTION",
        "constructor" : "CONSTRUCTOR",
        "int"         : "INT",
        "boolean"     : "BOOLEAN",
        "char"        : "CHAR",
        "void"        : "VOID",
        "var"         : "VAR",
        "static"      : "STATIC",
        "field"       : "FIELD",
        "let"         : "LET",
        "do"          : "DO",
        "if"          : "IF",
        "else"        : "ELSE",
        "while"       : "WHILE",
        "return"      : "RETURN",
        "true"        : "TRUE",
        "false"       : "FALSE",
        "null"        : "NULL",
        "this"        : "THIS"
    }
    
    def __init__(self, file):
        self.token_list = []
        self.cur_token  = ""
        self.t_idx = self.t_max = 0
        
        if os.path.isfile(file):
            fp = open(file)
            readlines = fp.readlines()
            for i in range(len(readlines)):
                line   = readlines[i]
                tokens = line.split()
                for j in range(len(tokens)):
                    self.token_list.append(tokens[j])
                self.t_max += len(tokens)
        fp.close()
        print("t_max = ", self.t_max)
        
        return

    def hasMoreTokens(self):
        return self.t_idx < self.t_max

    def advance(self):
        self.cur_token = self.token_list[self.t_idx]
        self.t_idx+=1
        return

    def tokenType(self):
        token = self.cur_token
        token_type = "NOT_TOKEN"        
        if( len(token) == 0):
            return "NOT_TOKEN"
            
        if token in self.tokenType_keyword:
            token_type = "KEYWORD"
        elif token in self.tokenType_keyword:            
            token_type = "SYMBOL"
        elif token.isdigit():
            int_token = int(token)
            if int_token >= 0 and int_token <= 32767:
                token_type = "INT_CONST"
        elif not ('"' in token and '\n' in token and '\r\n' in token):
            token_type = "STRING_CONST"
        elif not(token[:1].isdigit()):
            token_type = "IDENTIFIER"  
        else:
            token_type = "NOT_TOKEN"

        print("token = ", token, ", type = ", token_type)            
        return token_type

    def keyWord(self):
        keyword = self.cur_token.split()
        if( len(keyword) == 0):
            return "NOT_KEYWORD"
        
        keyword_head = keyword[0]
        keyword_type = self.keyWord.get(keyword_head, "NOT_KEYWORD")
        return keyword_type

    def symbol(self):
        # can call tokenType=SYMBOL
        return ''

    def identifier(self):
        # can call tokenType=IDENTIFIER
        return ""
    
    def intVal(self):
        # can call tokenType=INT_CONST
        return 0
    
    def stringVal(self):
        # can call tokenType=STRING_CONST
        return ""
    
