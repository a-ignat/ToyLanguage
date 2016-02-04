#!/usr/bin/env python
import paramiko
import os.path
import subprocess
import time
import sys
import re
import socket
import telnetlib
#Module for output coloring
from colorama import init, deinit, Fore, Style
#Initialize colorama
init()

class Router(object):
    '''Encapsulate ip validation and connection objects'''
    def __init__(self, ip, user, passwd, cmdfile, debug = False):
        self.ip = ip.strip()
        self.cmdfile = cmdfile
        self.password = passwd.strip()
        self.username = user.strip()
        self.debug = debug
        self.err = False
        self.err_des = ""
        self.output = ""
        self.cmd = ""
        #telnet connection is not restarted
        self.__reset__ = False
        
        
        #do checks
        self.__ip_is_valid__()
        self.__ping__()
        self.__cmd_is_valid__()
    
        #there was an error
        if self.err:
            print Fore.RED + "\nFirst correct errors!\n"
            #Back to normal window
            print(Style.RESET_ALL)
            return
        #self.__ssh_open__ = False #to be removed
        self.__ssh_open__ = self.__open_port__(22)
        self.__telnet_open__ = self.__open_port__(23)
        if self.__ssh_open__:
            self.__ssh__()
        elif self.__telnet_open__:
            self.__telnet__()
        else:
            print Fore.RED + "\n* No open ports on device: %s\n" % self.ip
            self.err = True
            self.err_des = "invalid ports"
            #Back to normal window
            print(Style.RESET_ALL)
        
    
    #Checking IP address validity
    def __ip_is_valid__(self):
        
        a = self.ip.split('.')
        if (len(a) == 4) and (1 <= int(a[0]) <= 223) and (int(a[0]) != 127) and (int(a[0]) != 169 or int(a[1]) != 254) and (0 <= int(a[1]) <= 255 and 0 <= int(a[2]) <= 255 and 0 <= int(a[3]) <= 255):
            return         
        else:
            print Fore.RED + "\n* This is INVALID IP address: %s\n" % self.ip
            self.err = True
            self.err_des = "invalid ip"
            #Back to normal window
            print(Style.RESET_ALL)
                
    #Check device reachability            
    def __ping__(self):
        ping_reply = subprocess.call(['ping', '-c', '2', '-w', '2', '-q', '-n', self.ip], stdout = subprocess.PIPE)
                
        if ping_reply == 0:
            return
                
        elif ping_reply == 2:
            print Fore.RED + "\n* No response from device %s.\n" % self.ip
            self.err = True
            self.err_des = "invalid ping"
                
        else:
            print Fore.RED + "\n* Ping to the following device has FAILED: %s\n" % self.ip
            self.err = True
            self.err_des = "invalid ping fail"
            #Back to normal window
            print(Style.RESET_ALL)
            
                
    #Checking command file validity
    def __cmd_is_valid__(self):
        if os.path.isfile(self.cmdfile) == True:
            return
            
        else:
            print Fore.RED + "\n* File %s does not exist!\n" % self.cmdfile
            self.err = True
            self.err_des = "invalid cmd"
            #Back to normal window
            print(Style.RESET_ALL)
    
    def __open_port__(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect((self.ip, port))
            s.close()
        except:
                #print "Open False"
                return False
        #print "Open True"
        return True
    
    def __ssh__(self):
        #create ssh connection
        
        if self.err:
            print Fore.RED + "\n* Please, correct errors!\n"
            #Back to normal window
            print(Style.RESET_ALL)
            return
        
        #connect to device
        try:
            def disable_paging(remote_conn):
                '''Disable paging on a Cisco router'''
            
                remote_conn.send("terminal length 0\n")
                time.sleep(0.5)

                # Clear the buffer on the screen
                output = remote_conn.recv(1000)
            
    

            # Create instance of SSHClient object
            #keep a reference no to be garbage collected
            self.__ssh_client__ = paramiko.SSHClient()
        
            # Automatically add untrusted hosts (make sure okay for security policy in your environment)
            self.__ssh_client__.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
            # initiate SSH connection
            self.__ssh_client__.connect(self.ip, username=self.username, password=self.password, look_for_keys=False)
        
            # Use invoke_shell to establish an 'interactive session'
            self.__connection__ = self.__ssh_client__.invoke_shell()
                     
            print "Interactive SSH session with %s established\n" % self.ip
        
            # Strip the initial router prompt
            drop = self.__connection__.recv(1000)
        
            # Turn off paging
            disable_paging(self.__connection__)
            #read commands
            cmd_file = open (self.cmdfile, 'r')
            self.__cmds__ = cmd_file.readlines()
            cmd_file.close()
            #print self.__cmds__
        except paramiko.AuthenticationException:
            print Fore.RED + "Invalid username or password\n"
            self.err = True
            self.err_desc = "invalid user/pass"
            #Back to normal window
            print(Style.RESET_ALL)
            
        except paramiko.SSHException:
            print Fore.RED + "SSH connection aborted by device\n"
            self.err = True
            self.err_desc = "invalid ssh"
            #Back to normal window
            print(Style.RESET_ALL)
        
            
            
    def __telnet__(self):
        #create telnet connection
        port = 23
        timeout = 1
        try:
            self.output = ""
            connection = telnetlib.Telnet(self.ip, port, timeout)
            self.__connection__ = connection
            #get username prompt
            drop = connection.read_until("sername:", timeout)
           
            #enter username
            connection.write(self.username + '\n')
            #get password prompt
            drop = connection.read_until("assword:", timeout)
            #print self.output
            connection.write(self.password + '\n')
            #check if login succeeded
            result = connection.read_until("#", 3)
            #if no device promt assume invalid user/pass
            if result[-1] != "#":
                print Fore.RED + "Invalid user or password: %s!" % self.ip
                self.erro = True
                self.err_des = "invalid user pass"
                #Back to normal window
                print(Style.RESET_ALL)
                return
            
            #login suceeded
            if not self.__reset__: print "Telnet connection with %s established.\n" % self.ip
            #disable pagination
            connection.write("terminal length 0\n")

            #clear buffer
            drop = connection.read_until('#', timeout)
            #read commands
            if not self.__reset__:
                #command are not read form file
                cmd_file = open (self.cmdfile, 'r')
                self.__cmds__ = cmd_file.readlines()
                cmd_file.close()
        except IOError:
            #unable to connect
            print Fore.RED + "Unable to telnet to %s!" % self.ip
            self.err = True
            self.err_des = "Invalid telnet session."
            #Back to normal window
            print(Style.RESET_ALL)
            
        
            
    def send(self, cmd): 
        if not self.__ssh_open__:
            #send throuh telnet
            self.__send_t__(cmd)
            return
        #send through ssh
        #self.chan.send(cmd+'\n')
        self.__connection__.send(cmd+'\n')
        
        time.sleep(0.7)
        #get ouput
        #output = self.chan.recv(5000)
        output = self.__connection__.recv(9999)
        #print "Router output: %s" % output
    
        #check for errors
        if re.findall(r"Invalid input", output) or re.findall(r"Incomplete command", output)or re.findall(r"Unknown command", output):
            print Fore.RED + "Error on device %s while executing: %s\n" % (self.ip, output)
            self.error = True
            self.output = output
            #Back to normal window
            print(Style.RESET_ALL)
            
        else:
           #no errors
            self.error = False

            if self.debug: print "Command is: %s" %cmd
            
            #get rid of the echoed commad
            output = output[output.find('\n'):]
            #get rid of the router prompt
            output = output[:output.rfind('\n')]
            output = output.strip()
            #add \r\n as sockets do at the end of line
            if output: output = output + '\r\n'
            if self.debug: print "Output is: %s" %output
            
            self.output = output
                
            
        
    def __send_t__(self, cmd):
        #telnet command
        self.output = ""
        self.cmd = cmd
        #print cmd
        self.__connection__.write(cmd + '\n')
        time.sleep(0.7)
        output = self.__connection__.read_until('#')
        drop = self.__connection__.read_very_eager()
        #print output
        #check for errors
        if re.findall(r"Invalid input", output) or re.findall(r"Incomplete command", output) or re.findall(r"Unknown command", output):
            print Fore.RED + "Error on device %s while executing: %s\n" % (self.ip, output)
            self.error = True
            self.output = output
            #Back to normal window
            print(Style.RESET_ALL)
            #close the connection beacause output is a mess
            self.__connection__.close()
            #restart it again without affecting next commands
            self.__reset__ = True
            self.__telnet__()
            
        else:
            #no errors
            self.error = False
            #get rid of the first line
            ind = output.find('\n')
            
            #get rid of the last line
            output = output[:output.rfind('\n')]
            self.output = output[ind + 1:]
            self.output = self.output.strip()
            #add \r\n as sockets do
            if self.output: self.output = self.output + '\r\n'
            
            if self.debug: print "Command is: %s" %cmd
            if self.debug: print "Output is: %s" % self.output
    
    def next_cmd(self, ):
        
        if len(self.__cmds__) == 0:
            print Fore.GREEN + "Done with device %s\n" % self.ip
            if self.__ssh_open__:
                self.__ssh_client__.close()
            else:
                #close telnet connection
                self.__connection__.close()
                
            #Back to normal window
            print(Style.RESET_ALL)
            return False
            
        #strip leading spaces
        cmd = self.__cmds__.pop(0)
        cmd = cmd.lstrip()

        #skip comments
        while  cmd.startswith('#'):
            if len(self.__cmds__) == 0:
                print Fore.GREEN + "Done with device %s\n" % self.ip
                if self.__ssh_open__:
                    self.__ssh_client__.close()
                else:
                    #close telnet connection
                    self.__connection__.close()
                #Back to normal window
                print(Style.RESET_ALL)
                return False
            cmd = self.__cmds__.pop(0).lstrip()
         
        return cmd
    
#De-initialize colorama
deinit()
#end of class
