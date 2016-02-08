#Example scripts

###Example 1
Checks if router has interface Loopback100.
If true the interface Loopback100 is configured with the description *has Lb100*.
If false the interface Loopback2 is configured with the description *does not have Lb100*.
>
`sh ip int br | in Loopback100`  
`<iff <get output>`  
`<the <cmd "conf t" ><cmd "int Loop100" ><cmd "descr has Lb100" >>`  
`<els <cmd "conf t" ><cmd "int Loop2" ><cmd "descr does not have Lb100" >>>`  
`end`  

###Example 2
Extracts the hardware MAC address of interface Fa0/0 of each device and appends it to a file named *MACs.txt*
> 
`sh int fa0/0 | in Hardware`  
`<exp MACs.txt <get output>>`  


###Example 3
Configures interface Loopback10 on each device with an IP address.
The IP address is read from a file named *lbs.txt*. The file has the format: *IP=x.x.x.x*.
The line that starts with the IP equal to the current device IP (`env['ip']`) is read 
and the corresponding value x.x.x.x is used for the Loopback.
> 
`conf t`  
`int Loo10`  
`<cmd "ip address " + <imp lbs.txt > + " 255.255.255.0">`  
`end`  

###Example 4
Black-holes the source IP that sends traffic more than 100 packets through interface Fa0/0.
By changing the regexp pattern, traffic quantity can be easily changed to KB, MB or GB.
After getting the result for IP flows from router it is assigned to variable *cache*.
Then using regexp the matched traffic quantity is assigned to variable *pkts*. The corresponding 
source IP is assigned to variable *src*. If traffic quantity exceeds the specified threshold,
a command is constructed to null route the traffic source.
If not both pattern matches fail and array index out of range message is printed.
If multiple matches are produced the first match is black-holed.
> 
`show ip cache flow | in Fa0/0`  
`<set cache <get output>>`  
`<evl "re.findall(r'^\w+\d\/\d\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+.+?(\d\d\d+) \r\n', self.env['cache'], re.MULTILINE)[0][1]" >`  
`<set pkts <get output >>`  
`<evl "re.findall(r'^\w+\d\/\d\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+.+?(\d\d\d+) \r\n', self.env['cache'], re.MULTILINE)[0][0]" >`  
`<set src <get output>>`  
`<iff <get pkts >`  
`<the <cmd "conf t" > <cmd "ip route " + <get src> + " 255.255.255.255 null0">>>`  

###Example 5
Probably a better variant of Example 4.
In this example the router does the first pattern matching and filters only IP sources generating more than 100 packets
and coming through interface Fa0/0.
The second line pattern matches the first IP source address and stores the result in *src* variable.
Then generates and sends router command to black-hole the source.
>
`sh ip cache flow | in Fa0/0.+[1-9][0-9][0-9]+`  
`<evl "re.findall(r'^\w+\d\/\d\s+ \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+.+?(\d\d\d+) \r\n', self.env['output'], re.MULTILINE)[0][0]" >`  
`<set src <get output >>`  
`<cmd "conf t" >`  
`<cmd "ip route " + <get src> + " 255.255.255.255 null0" >`  

###Example 6
The same example implemented using `<reg >` construct. Do source and traffic pattern matching on one line. 
>
`show ip cache flow | in Fa0/0`  
`<reg "^\w+\d\/\d\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+.+?(\d\d\d+) \r\n" <get output >>`  
`<set pkts <get match[0][1] >>`  
`<set src <get match[0][0] >>`  
`<iff <get pkts >`  
`<the <cmd "conf t" > <cmd "ip route " + <get src> + " 255.255.255.255 null0">>>`   



###Example 7
Nested <iff ... > constructs.
All nested <iff ...>, <the ...> or <els ...> clauses must span a single line. The number of trailing **>** is increased by one for each *<the*, *<els*
or *<iff* clause. In this example two *<iff* + two *<the* + one for the *<set* construct adds up to 5. As a result the variable **t** is set to **True**,
>  
`<set test "good" >`  
`<iff <get test>`  
`<the <iff "True" <the <set t "pass" >>>>>`  
