#More scripts

###Policy routing
In this example all traffic sourced from IP 192.168.2.10 is policy routed to host 10.10.10.10,
regardless of destination address. All routing devices are configured in one pass.
*First* is determined the incoming interface facing host 192.168.2.10.
*Second* is determined the next-hop router for destination 10.10.10.10.
*Third* is configured an access-list to match traffic coming from source 192.168.2.10.
*Fourth* is configured a route map using the access-list which sets the next-hop to the IP
determined in *step 2*.
*At last* the route-map is applied to the interface determined in *step 1*.
The router to which 10.10.10.10 is directly connected should not be included in device configuration IPs,
beacause in that case policy routing is pointless. Besides next-hop match will produce an empty string,
causing an error during execution.
Sample generated configuration commands may look-like this:
>
ip access-list extended host_10
 permit ip host 192.168.2.10 any

route-map my_map permit 10
 match ip address host_10
 set ip next-hop 172.16.0.2

interface FastEthernet0/0
 ip policy route-map my_map
 
*Actual script:*
>
`sh ip route 192.168.2.10 longer-prefixes | in [0-9]\/[0-9]`
`<reg " (\w+\/\w+.*)\r\n" <get output >>`
`<set in_int <get match[0] >>`
`sh ip route 10.10.10.10 longer-prefixes | in [0-9]\/[0-9]`
`<reg "via (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})" <get output >>`
`<set next_hop <get match[0] >>`
`conf t`
`ip access-list extended host_10`
`permit ip host 192.168.2.10 any`
`route-map my_map`
`match ip address host_10`
`<cmd "set ip next-hop " + <get next_hop >>`
`<cmd "int " + <get in_int>>`
`ip policy route-map my_map`
`end`  