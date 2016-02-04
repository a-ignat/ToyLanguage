#!/usr/bin/env python

import threading
import re
import sys
import os.path

#Router module with Router class
from Router import Router
#Interpreter module with Interpreter class
from Interpreter import Interpreter

#require Router object debug
rdeb = False
#reguire Interpreter object debug
ideb = False
    
def create_dev(ip):
    dev = Router(ip, username, password, cmd_file, rdeb)
    if dev.err:
        print "Skipping device %s\n" %ip
        return
    #all input values are correct
    #create Interpreter
    i = Interpreter(dev, ideb, ideb)
    i.start()
    if ideb:
        #print last debug info
        print "Oper_st: %s" %i.oper_st
        print "Data_st: %s" %i.data_st
        print "Env: %s" %i.env
    
#    #print cmd
#    while cmd:
#        try:
#            #execute the command
#            i.line = cmd
#            i.parse_line()
#            if dev.do : dev.send(dev.do); dev.do = ""
#            #print dev.output
#            #get next
#            cmd = dev.next_cmd()
#        except KeyboardInterrupt:
#            #allow user to stop execution
#            print "Program aborted by user.\n"
#            sys.exit()

#check command line arguments
args = sys.argv
argc = len(args)

if argc == 1: #no arguments
    #proceed with code bellow if
    pass
elif argc == 2: #one argument => debug router commands/response and interpreter
    if args[1] != '-d' and args[1] != '-dd': print "Usage: Rtrcfg -d =>for Router debug or \nRtrcfg -dd =>for Router and Interpreter debug or \nRtrcfg -d|-dd cmd_file =>for Interpreter debug"; sys.exit()
    #require router object debug
    if args[1] == '-d': rdeb = True
    #alseo require Interpreter debug, really desparate
    if args[1] == '-dd': ideb = True
elif argc == 3: #two arguments =>create dummy Router object and debug
    if args[1] != "-d" and args[1] != "-dd":  print "Usage: Rtrcfg -d =>for Router debug or \nRtrcfg -dd =>for Router and Interpreter debug or \nRtrcfg -d|-dd cmd_file =>for Interpreter debug"; sys.exit()
    if not os.path.isfile(args[2]) == True: print "The file %s does not exist!" % args[2];sys.exit()
    #read file
    f = open(args[2], 'r')
    cmds = f.readlines()
    f.close()
    #set verbose debug if -dd
    verbose = args[1] == '-dd'
    #define dummy Router class
    class Dummy(object):
        def __init__(self, ):
            self.ip = '192.168.0.1'
            self.output = 'Dummy output'
            self.cmds = cmds
        
        def send(self, cmd):
            pass
        
        def next_cmd(self, ):
            if len(self.cmds) == 0:
                print "Done with device\n"
                return False
                
            #strip leading spaces
            cmd = self.cmds.pop(0)
            cmd = cmd.lstrip()
            #skip comments
            while  cmd.startswith('#'):
                if len(self.cmds) == 0:
                    print "Done with device \n"
                    return False
                cmd = self.cmds.pop(0).lstrip()
            return cmd
    #end of Dummy class
    #instantiate Dummy
    r = Dummy()
    #instantiate Interpreter and set debug
    i = Interpreter(r, debug = True, verb = verbose)
    i.start()
    print "Oper_st: %s" %i.oper_st
    print "Data_st: %s" %i.data_st
    #print env after last command if required
    if verbose: print "Env: %s" %i.env
    #work is done end
    sys.exit()   

else : #wrong command
    print "Usage: Rtrcfg -d =>for Router debug or Rtrcfg -d|-dd cmd_file =>for Interpreter debug"; sys.exit()

#list with device ips
ip_list = []

#get ips        
ip_file = raw_input("Enter IP file or an IP: ")
if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ip_file):
    #one ip
    ip_list.append(ip_file)
else:
    #a file with IPs
    try:
        #Open user selected file for reading (IP addresses file)
        f = open(ip_file, 'r')
        #Starting from the beginning of the file
        f.seek(0)
        #Reading each line (IP address) in the file
        ip_list = f.readlines()
        #Closing the file
        f.close()
    except IOError:
        print "File %s does not exist!\n" % ip_file
        sys.exit()

#get username
username = raw_input("Enter Username: ")

#get password
password = raw_input("Enter Password: ")

#get commands
cmd_file = raw_input("Enter file with commands: ")

def create_threads():
    threads = []
    for ip in ip_list:
        th = threading.Thread(target = create_dev, args = (ip,))
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
#Calling threads creation function
create_threads()

    


#End of program


