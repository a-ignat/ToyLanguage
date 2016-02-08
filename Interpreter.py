#!/usr/bin/env python
import re
import sys
import os.path
from Router import Router

class Interpreter(object):
    ''' Parses and executes each line of router commands'''
    def __init__(self, Router, debug = False, verb = False):
        self.__Router__ = Router
        self.env = {}
        #print debug data if required default is not
        self.debug = debug
        #print self.env{} for debug
        self.verbose = verb
        #operation stack
        self.oper_st = []
        #data stack
        self.data_st = []
        #match object
        self.env['match'] = ""
        # to identify this router
        self.env['ip'] = self.__Router__.ip
        
    def start(self,):
        #do all commands
        line = self.__Router__.next_cmd()
        while line:
            self.line = line
            try:
                self.parse_line()
            except KeyboardInterrupt:
                #allow user to stop execution
                print "Program aborted by user.\n"
                sys.exit()
            line = self.__Router__.next_cmd()
            
    def parse_line(self, ):
        
        while len(self.line) > 0:
            self.line = self.line.strip()
            if self.debug:
                #if verbose debug
                if self.verbose: print "Env: %s" % self.env
                #print debug information
                print "Line: %s" % self.line
                print "Oper_st: %s " % self.oper_st
                print "Data_st: %s \n" % self.data_st
                
            if len(self.line) == 0: return True
            #get first character
            char = self.line[:1]
            if char == ">":
                #do top operation
                self.eval()
                #get rid of the first char
                self.line = self.line[1:]
                #recurse
                self.parse_line()
                
            elif char == "\"" :
                #get what is between qoutes and put in data_st
                m = re.match(r"\"(.+?)\"", self.line)
                if m:
                    self.data_st.append(m.groups(0)[0])
                    #no escape of special symbols
                    #get the remainder of the line and recurse
                    self.line = self.line[len(m.group()):]
                    self.parse_line()
                else:
                    self.data_st.append("")
                    #strip the qoutes
                    self.line = self.line[2:]
                    self.parse_line()
            #################
            elif char == "\'" :
                #get what is between qoutes and put in data_st
                m = re.match(r"\'(.+?)\'", self.line)
                if m:
                    self.data_st.append(m.groups(0)[0])
                    #avoid double escaping the special characters for special characters
                    self.data_st[-1] = self.data_st[-1].decode('string_escape')
                    #get the remainder of the line and recurse
                    self.line = self.line[len(m.group()):]
                    self.parse_line()
                else:
                    self.data_st.append("")
                    #strip the qoutes
                    self.line = self.line[2:]
                    self.parse_line()
            ##############
                
            elif self.line.startswith('+ '):
                #string concatenation op1 + op2, op1 is evaluated evaluate op2 and do concatenation
                #strip +
                self.line = self.line[2:]
                #this is syntactic sugar, convert to <con...> form
                #put command in stack
                self.oper_st.append('con')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()
                
            elif self.line.startswith('and '):
                #op1 and op2, op1 is evaluated, eval op2 if needed do and put result in data_st
                #strip and
                self.line = self.line[4:]
                #this is syntactic sugar, convert to <and...> form
                #put command in stack
                self.oper_st.append('and')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()
            
            elif self.line.startswith('== ') :
                #op1 equals op2, op1 is evaluated, eval op2 do comparison and put result in data_st
                
                #strip == 
                self.line = self.line[3:]
                #this is syntactic sugar, convert to <equ...> form
                #put command in stack
                self.oper_st.append('equ')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()
            
            elif self.line.startswith('!= ') :
                #actually two commands =>invert the result of equal command
                
                #strip != 
                self.line = self.line[3:]
                #this is syntactic sugar, convert to <not...> of result of <equ...>
                #first add not operation to stack to be executed after equal
                self.oper_st.append('not')
                #add > to trigger the command
                self.line = self.line + '>'
                #put equ command in stack
                self.oper_st.append('equ')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()    
            
            elif self.line.startswith('ge ') :# or self.line.startswith('le '):
                #string comparison greater than op1 > op2
                
                #strip ge
                self.line = self.line[3:]
                #this is syntactic sugar, convert to <gre...> form
                #put command in stack
                self.oper_st.append('gre')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()
            
            elif self.line.startswith('le ') :
                #string comparison less than op1 < op2
                
                #strip ge
                self.line = self.line[3:]
                #this is syntactic sugar, convert to <les...> form
                #put command in stack
                self.oper_st.append('les')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()
            
            elif self.line.startswith('or '):
                #op1 or op2, op1 is evaluated, eval op2 if needed and put result in data_st
                
                #strip or
                self.line = self.line[3:]
                #this is syntactic sugar, convert to <orr...> form
                #put command in stack
                self.oper_st.append('or')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()
            
            elif self.line.startswith('not '):
                #evaluate the remainder of the line and invert
                
                #strip not
                self.line = self.line[4:]
                #this is syntactic sugar, convert to <not...> form
                #put command in stack
                self.oper_st.append('not')
                #add > to trigger the command
                self.line = self.line + '>'
                #evaluate next
                self.parse_line()
            
            elif char !="<":
                #it must be command to router
                if self.debug:
                    print "    sending command: %s" % self.line   
                self.__Router__.send(self.line)
                self.env['output'] = self.__Router__.output
                #done with line so reutrn
                return
            
            elif char == "<":
                #special construct
                #get first for chars of the line
                fours = self.line[:5]
                if fours == '<get ':
                    #<get name> -get the value of the variable
                    m = re.match(r"<get ([\w\[\]]+) ?", self.line)
                    if not m: print "Wrong get syntax: % s\n" % self.line; sys.exit()
                    name = m.groups(0)[0]
                    #push command to command stack
                    self.oper_st.append("get")
                    #push var name to data stack
                    self.data_st.append(name)
                    #strip match and recurse
                    self.line = self.line[len(m.group()):]
                    self.parse_line()
                elif fours == '<set ':
                    #<set name "value">
                    m = re.match(r"<set ([\w\[\]]+) ?", self.line)
                    if not m: print "Wrong set syntax: % s\n" % self.line; sys.exit()
                    name = m.groups(0)[0]
                    #push command to command stack
                    self.oper_st.append("set")             
                    #push var name to data stack
                    self.data_st.append(name)
                    #strip match and recurse
                    self.line = self.line[len(m.group()):]
                    #value will be evaluated next
                    self.parse_line()
                    
                elif fours == '<evl ':
                    #<evl expression> eval(expression) and put result in self.env[_output_]
                    #strip <evl
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("evl")             
                    #evaluate the expression
                    self.parse_line()
                
                elif fours == '<cmd ':
                    #<cmd "command" ->send command to router
                    #strip <cmd
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("cmd")             
                    #proceed
                    self.parse_line()
                    
                elif fours == '<con ':
                    #<con op2> ->string concatenation, op1 is in stack, op2 to be evaluated
                    #strip <con
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("con")             
                    #proceed
                    self.parse_line()      
                
                elif fours == '<and ':
                    #op1 op2 <and >  or <and op2> or <and op1 op2> ->logical and operators are in stack or to be evaluated
                    #strip <and
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("and")             
                    #proceed
                    self.parse_line()      
                    
                elif fours == '<orr ':
                    #op1 op2 <orr >  or <orr op2> or <orr op1 op2> ->logical or operators are in stack or to be evaluated
                    #strip <orr
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("or")             
                    #proceed
                    self.parse_line() 
                
                elif fours == '<not ':
                    #op1 <not >  or <not op1> ->logical not operator is in stack or to be evaluated
                    #strip <not
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("not")             
                    #proceed
                    self.parse_line()
                
                elif fours == '<gre ':
                    #op1 op2 <gre >  or op1 <gre op2>  or <gre op1 op2>->greater than string comparison  op1, op2 in stack or to be evaluated
                    #strip <gre
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("gre")             
                    #proceed
                    self.parse_line()
                    
                elif fours == '<les ':
                    #op1 op2 <les>  or op1 <les op2>  or <les op1 op2>->greater than string comparison  op1, op2 in stack or to be evaluated
                    #strip <gre
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("les")             
                    #proceed
                    self.parse_line()
                
                elif fours == '<equ ':
                    #op1 op2 <equ>  or op1 <equ op2>  or <equ op1 op2>->equals, string comparison  op1, op2 in stack or to be evaluated
                    #strip <equ
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("equ")             
                    #proceed
                    self.parse_line()
                
                elif fours == '<iff ':
                    #<iff cond <the line>> optional[<els line>>] or cond <iff ...... Evaluate condition and take true or false branch. Each on separate line
                    #strip <iff
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("if")             
                    #proceed
                    self.parse_line()
                    
                elif fours == '<the ':
                    #<iff cond <the line>> optional[<els line>>] or cond <iff ...... put true branch in data stack without evaluation. Whole line is the true branch
                    #strip nothing
                    #check if there is "if" at top of oper_st
                    if self.oper_st[-1] != "if": print "Then without <iff clause: %s" % self.line; sys.exit()
                                
                    #check if <> are balanced
                    lthan = self.line.count('<')
                    gthan = self.line.count('>')
                    diff = gthan - lthan
                    #print "DIFF: %s " %diff
                    if diff > 0:
                        #trigger evaluation, no unfinished operation in stack and there is no else clause.
                        #push line to data stack consuming one operation
                        self.data_st.append(self.line[:-1]) 
                        self.line = '>'
                        self.parse_line()
                    else:
                        #there is an else clause, do nothing
                        #push line to data stack
                        self.data_st.append(self.line) 
                        self.line = ""
                        return
                    
                
                elif fours == '<els ':
                    #<iff cond <the line>> optional[<els line>>] or cond <iff ...... put false branch in data stack without evaluation. Whole line is the false branch
                    #strip nothing
                    #check if there is "if" at top of oper_st and <els at the data_st
                    if self.oper_st[-1] != "if": print "Else without <iff clause: %s" % self.line; sys.exit()
                    if not self.data_st[-1].startswith('<the '): print "Else without <the clause: %s" % self.line; sys.exit()
                    #else clause is last; so it must end with >> to finish if clause
                    if not self.line.endswith('>'): print "Else clause must end with >: %s " % self.line; sys.exit()
                    
                    #push line to data stack consuming one operation
                    self.data_st.append(self.line[:-1])             
                    #trigger evaluation
                    self.line = '>'
                    self.parse_line()
                
                elif fours == '<imp ':
                    #<imp f_name > read from file with name f_name line that starts with self.env['ip'] and store in self.data_st and self.env[f_name]
                    m = re.match(r"<imp (\w+\.\w+) ", self.line)
                    if not m: print "Wrong imp syntax: % s\n" % self.line; sys.exit()
                    f_name = m.groups(0)[0]
                    #check if file exists
                    if not os.path.isfile(f_name) == True: print "The file %s does not exist!" %f_name; sys.exit()
                    
                    #push command to command stack
                    self.oper_st.append("imp")             
                    #push file name to data stack
                    self.data_st.append(f_name)
                    #strip match and recurse
                    self.line = self.line[len(m.group()):]  
                    #proceed
                    self.parse_line()
                    
                elif fours == '<exp ':
                    #<exp f_name value> evaluate value and append it to file with name f_name and set self.env[f_name]=value
                    m = re.match(r"<exp (\w+\.\w+) ", self.line)
                    if not m: print "Wrong exp syntax: % s\n" % self.line; sys.exit()
                    f_name = m.groups(0)[0]
                    
                    #push command to command stack
                    self.oper_st.append("exp")             
                    #push file name to data stack
                    self.data_st.append(f_name)
                    #strip match and recurse
                    self.line = self.line[len(m.group()):]  
                    #proceed
                    self.parse_line()
                    
                elif fours == '<reg ':
                    #<reg "pattern" string >| "pattern" <reg string> | "pattern" string <reg > match the pattern against the string. String can be variable or "value". Store the match in self.env['match']
                    #internally is used python's re.findall() with re.MULTILINE
                    #strip <reg
                    self.line = self.line[5:]
                    #push command to command stack
                    self.oper_st.append("reg")             
                    #proceed
                    self.parse_line()      
                
                    
                else :
                    #unknown construct <xxx 
                    print "Unknown construct: %s \n" %fours
                    sys.exit()
                    
                    
            else:
                #unknown command
                print "Unknown command % s\n" % self.line
                sys.exit()
                         
    
    
    
    
    def eval(self, ):
        if len(self.oper_st) < 1: print "Empty command stack!"; sys.exit()
        cmd = self.oper_st.pop()
        
        if cmd == 'get':
            #get a var from the environment
            #get var name
            if len(self.data_st) < 1: print "No name for get!"; sys.exit()
            name = self.data_st.pop()
            #check if exists
            if not name in self.env.keys(): print "No variable with name: %s \n" % name; sys.exit()
            value = self.env[name]
            self.data_st.append(value)
            
        elif cmd == 'set':
            #bind a variable to value
            if len(self.data_st) < 1: print "No value for set!"; sys.exit()
            value = self.data_st.pop()
            if len(self.data_st) < 1: print "No name for variable: %s \n" % name; sys.exit()
            name = self.data_st.pop()
            self.env[name] = value
            #print self.env[name]
            
        elif cmd == 'evl':
            #evaluate python expression
            if len(self.data_st) < 1: print "Not enough operands for <evl!"; sys.exit()
            exp = self.data_st.pop()
            try:
                result = eval(exp)
            except Exception as e:
                #choose not to break on errors. Instead report and set output to ""
                print "Error: %s" %e.message
                result = ""
            self.env["output"] = result
            #print self.env["output"]
            
        elif cmd == 'cmd':
            #send command to router and store result in self.env["_output_"]
            if len(self.data_st) < 1: print "Not enough operands for command!"; sys.exit()
            command = self.data_st.pop()
            #send command to router
            if self.debug:
                    print "    sending command: %s" % command
            self.__Router__.send(command)
            self.env['output'] = self.__Router__.output
               
        elif cmd == 'con':
            #string concatenation
            if len(self.data_st) < 2: print "Not enough operands for concatenation!"; sys.exit()
            op1 = self.data_st.pop()
            op2 = self.data_st.pop()
            result = op2 + op1
            self.data_st.append(result)
        
        elif cmd == 'and':
            #logical and
            if len(self.data_st) < 2: print "Not enough operands for <and!"; sys.exit()
            op1 = self.data_st.pop()
            #convert from string to boolean
            if op1 == "False":op1 = False
            op2 = self.data_st.pop()
            #convert from string to boolean
            if op2 == "False":op2 = False
            if op1 and op2:
                result = True
            else:
                result = False
                
            self.data_st.append(result)
            
        elif cmd == 'or':
            #logical or
            if len(self.data_st) < 2: print "Not enough operands for <and!"; sys.exit()
            #operators come in reverse order
            op2 = self.data_st.pop()
            #convert from string to boolean
            if op2 == "False":op2 = False
            op1 = self.data_st.pop()
            #convert from string to boolean
            if op1 == "False":op1 = False
            if op1 or op2:
                result = True
            else:
                result = False
                
            self.data_st.append(result)    
        
        elif cmd == 'not':
            #invertion
            if len(self.data_st) < 1: print "Not enough operands for invertion!"; sys.exit()
            op1 = self.data_st.pop()
            #convert from string to boolean
            if op1 == "False":op1 = False
            result = not op1
            self.data_st.append(result)
            
        elif cmd == 'gre':
            #string comparison s1 > s2, come in revese order
            if len(self.data_st) < 2: print "Not enough operands for <gre!"; sys.exit()
            #operators come in reverse order
            s2 = self.data_st.pop()
            #convert from string to boolean
            if s2 == "False":s2 = False
            s1 = self.data_st.pop()
            #convert from string to boolean
            if s1 == "False":s1 = False
            result = s1 > s2
                
            self.data_st.append(result)
            
        elif cmd == 'les':
            #string comparison s1 < s2, come in revese order
            if len(self.data_st) < 2: print "Not enough operands for <les!"; sys.exit()
            #operators come in reverse order
            s2 = self.data_st.pop()
            #convert from string to boolean
            if s2 == "False":s2 = False
            s1 = self.data_st.pop()
            #convert from string to boolean
            if s1 == "False":s1 = False
            result = s1 < s2
                
            self.data_st.append(result)
            
        elif cmd == 'equ':
            #string comparison s1 = s2, order no matter
            if len(self.data_st) < 2: print "Not enough operands for <equ!"; sys.exit()
            #operators come in reverse order
            s2 = self.data_st.pop()
            #convert from string to boolean
            if s2 == "False":s2 = False
            s1 = self.data_st.pop()
            #convert from string to boolean
            if s1 == "False":s1 = False
            result = s1 == s2
                
            self.data_st.append(result)    
        
        elif cmd == 'if':
            #in data_stack there must be optional false branch, true branch and evaluated condition
            if len(self.data_st) < 2: print "Not enough operands for <iff"; sys.exit()
            #read first branch
            branch = self.data_st.pop()
            if branch.startswith('<els '):
                #has true branch and false branch
                if len(self.data_st) < 2: print "Not enough operands for <els"; sys.exit()
                f_branch = branch
                t_branch = self.data_st.pop()
                cond = self.data_st.pop()
                #convert from string to boolean
                if cond == "False":cond = False
                
                if cond: #must execute t_branch
                    #strip <the
                    t_branch = t_branch[5:]
                    #strip >
                    t_branch = t_branch[:-1]
                    #evaluate the line
                    self.line = t_branch
                    self.parse_line()
                else: #must execute f_branch
                    #strip <the
                    f_branch = f_branch[5:]
                    #strip >
                    f_branch = f_branch[:-1]
                    #evaluate the line
                    self.line = f_branch
                    self.parse_line()
            else:
                #has only true branch
                if not branch.startswith('<the '): print "No then clause given after if!"; sys.exit()
                cond = self.data_st.pop()
                #convert from string to boolean
                if cond == "False":cond = False
                
                if cond: #condition is true execute the branch
                    t_branch = branch
                    #strip <the
                    t_branch = t_branch[5:]
                    #strip >>
                    t_branch = t_branch[:-1]
                    #evaluate the line
                    self.line = t_branch
                    self.parse_line()
                #else nothing to do more
         
        elif cmd == 'imp':
            #read variable from file
            if len(self.data_st) < 1: print "Not enough operands for <imp !"; sys.exit()
            #read file name
            f_name = self.data_st.pop()
            #open file
            f = open(f_name, 'r')
            lines = f.readlines()
            f.close()
            found = False
            for line in lines:
                ip, value = line.split('=')
                if ip == self.env['ip']:
                    #get rid of spaces and new lines
                    value = value.strip()
                    self.env[f_name] = value
                    self.data_st.append(value)
                    found = True
            #check if we read data
            if not found: print "Could not find ip %s in file %s" %(self.env['ip'], f_name); sys.exit()
            #done with import
            
        elif cmd == 'exp':
            #read variable from file
            if len(self.data_st) < 2: print "Not enough operands for <exp !"; sys.exit()
            #read value
            value = self.data_st.pop()
            #read file name
            f_name = self.data_st.pop()
            #open file
            f = open(f_name, 'a+')
            line = self.env['ip'] + '=' + value
            if line[-1] != '\n': line = line + '\n'
            f.write(line)
            f.close()
            self.env[f_name] = value    
        
        elif cmd == 'reg':
            #match regexp
            if len(self.data_st) < 2: print "Not enough operands for <reg !"; sys.exit()
            #read string
            string = self.data_st.pop()
            #read pattern
            pattern = self.data_st.pop()
            pattern = r"" + pattern + r""
            #initialize env[match]
            for key in self.env.keys():
                if key.startswith('match'):
                    self.env.pop(key)
            
            match = re.findall(pattern, string, re.MULTILINE)
            if not match: #no match
                self.env['match'] = ''; return
            #there is a match
            if type(match[0]) is str: #match is a list
                for i in range(len(match)):
                    self.env["match" + "[" + str(i) + "]"] = match[i]
            else: #match is a list of tuples
                for i in range(len(match)):
                    for j in range(len(match[0])):
                        self.env["match"+"["+str(i)+"]["+str(j)+"]"] = match[i][j]
                
            
        else:
            #unknow commmand
            print "Unknow operation: %s" %cmd; sys.exit()
            
