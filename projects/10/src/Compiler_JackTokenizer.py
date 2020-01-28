import os
import sys
import glob
import pprint
import re  # for re.split

class JackTokenizer:

    # keyworkd, symbol are terminal of Jack
    terminal_keyword = ['class', 'constructor', 'function',
                        'method', 'field', 'static', 'var',
                        'int', 'char', 'boolean', 'void',
                        'true', 'false', 'null', 'this',
                        'let', 'do', 'if', 'else',
                        'while', 'return']                         
    terminal_symbol = ['{', '}', '(', ')', '[', ']', '.', ',',
                       ';', '+', '-', '*', '/', '&',
                       '|', '<', '>', '=', '~']
    term_symbol_regexp = '([' + re.escape('{}()[].,;\+-*/&|<>=~') + '])'
     
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
            skip_endcomment = False
            for i in range(len(readlines)):
                line  = readlines[i]
                words = self.splitLine2Words(line)                
                skip_endline = False
                
                for j in range(len(words)):
                    # isComments
                    if words[j] == "//":
                        skip_endline = True # skip this line
                        continue                        
                    elif words[j] == "/**" or words[j] == "/*":
                        skip_endcomment = True  # skip until */ found
                    elif skip_endcomment and words[j] == "*/":
                        skip_endcomment = False # end of comments
                        continue
                        
                    if (not skip_endline) and (not skip_endcomment):
                        self.t_max += self.cvtWords2Token(words[j], self.token_list)
        fp.close()
        
        return

    def splitLine2Words(self, line):
        '''
        separate line to words by space and '\n'.
        But double_quoted word (like "hoge piyo") exceptionally treat as a word.
        '''
        words = []
        w_start = dquote_start = 0
        isWord = isDquote = False
        line = line.strip() # remove head and tail spaces and '\n'
        for i in range(len(line)):
            if line[i] == '"':
                # is double_quoted string?                
                if isDquote == False:
                    dquote_start = i
                    isDquote = True
                else:
                    word = line[dquote_start:i+1]
                    words.append(word)
                    dquote_start = 0
                    isDquote = False                    
            elif isDquote == False:
                # separate by space
                if line[i] != r' ' and isWord == False:
                    w_start = i
                    isWord  = True
                    
                if (line[i] == r' ' or i == len(line)-1) and isWord == True:
                    w_end = i
                    if i == len(line)-1:                    
                        w_end = i+1
                    word = line[w_start:w_end] 
                    words.append(word)
                    w_start = 0
                    isWord = False
                    
        return words
    
    def cvtWords2Token(self, words, token_list):
        '''
        separate words by term_symbol_regexp, and treat each of them as a token.
        '''
        token_cnt = 0
        separated_w = re.split(self.term_symbol_regexp, words)
        for i in range(len(separated_w)):
            if len(separated_w[i]) > 0:
                token_list.append(separated_w[i])
                token_cnt += 1

        return token_cnt
    
    def hasMoreTokens(self):
        return self.t_idx < self.t_max

    def advance(self):
        self.cur_token = self.token_list[self.t_idx]
        self.t_idx+=1
        return

    def tokenType(self):
        token = self.cur_token
        token_type = "NON_TERMINAL"        
            
        if token in self.terminal_keyword:
            token_type = "KEYWORD"
        elif token in self.terminal_symbol: 
            token_type = "SYMBOL"
        elif token.isdigit():
            int_token = int(token)
            if int_token >= 0 and int_token <= 32767:
                token_type = "INT_CONST"
        elif token[0] == '"' and not (token in ['\n', '\r\n']):
            token_type = "STRING_CONST"
        elif not(token[0].isdigit()):
            token_type = "IDENTIFIER"  
        else:
            token_type = "NON_TERMINAL"

        return token_type

    def keyWord(self):
        return self.keyWord_dict.get(self.cur_token, "INVALID_KEYWORD")

    def symbol(self):
        # can call tokenType=SYMBOL
        return self.cur_token

    def identifier(self):
        # can call tokenType=IDENTIFIER
        return self.cur_token
    
    def intVal(self):
        # can call tokenType=INT_CONST
        ret = 0
        if self.cur_token.isdigit:
            ret = int(self.cur_token)
        return ret
    
    def stringVal(self):
        # can call tokenType=STRING_CONST
        rm_dquote_token = self.cur_token.strip('"') # remove double quote from token
        return rm_dquote_token
    
