#Router toy language

>A very simple language for interacting with Cisco devices. More information can be found in **Language Expressions**.
Based on Python as meta language. Before connecting to a device some preliminary checks are executed:

1. *If the provided IP address is valid.*
2. *If the IP is ping reachable.*
3. *If the provided command file exists.*
4. *If ssh or telnet port is open.*

If **open** ssh port is detected the program uses **ssh** protocol to connect. If not it checks for **open** telnet port and uses **telnet** protocol to connect. If both checks fail program quits with an error message.

Each device is created in a separate thread with one **Router** and one **Interpreter** objects.
Devices are specified when starting the program either as a single IP or a list of IPs in a text file. In the file every IP occupies a separate line. User must provide *username* and *password* for privileged access.
User also must provide file name with *language expressions* for execution **(command file)**.


##Debugging

###Debugging Interpreter object
####First option
* Use command: `Rtrcfg -d command_file,` where `command_file` is the path to the file for processing. Each parser function iteration prints to terminal the line being processed, command stack and operand stack.
During debugging a dummy Router object is created and no connection is set up.
No commands are sent and the `Router.output` field is set to "Dummy output".
Useful for checking command syntax during script execution.

####Second option
* Use command: `Rtrcfg -dd command_file.`
Same as the first option but also prints the current environment stored in `env` hash.


###Debugging Router object
####First option
* Use command: `Rtrcfg -d.`
Creates Router, Interpreter objects and connects to device(s).
Prints to terminal commands sent to and responses received from device.
Useful to see what the script is actually doing.

####Second option
* Use command: `Rtrcfg -dd.`
Enables debugging for both Router and Interpreter objects. 
Enables the second option for Interpreter debug. Useful for testing with real data when something is going wrong. Very verbose and should be used only when fixing mistakes.

Author: a_ignatov@abv.bg