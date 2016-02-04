#Language Expressions

There are two types of values: **strings** and **booleans**. When doing logical operations booleans are assumed.
All string values are treated as `True` except the empty string `""` and the string `False`.

* **environment** - implemented by hash table for storing variables. Initialized with `ip:router_ip_address`. To read a variable value use: `<get v_name>`. To store a variable value use: `<set v_name value>`

##Syntax, Semantics, Evaluation

1. `"string"` or `'string'` - a value equal to the string enclosed between double/single qoutes. Stored to data stack. Evaluates to itself.
2. `<get v_name >` - read the value of variable with name **v_name**. A variable can be bound only to strings or booleans. 
When evaluated, reads from the environment the value stored under the **key v_name** and pushes it to data stack.
3. `<set v_name e >` - evaluate the expression **e** and store the string/boolean value in environment under the key **v_name**.
4. `<imp f_name >` - reads from file with name **f_name** the line that starts with environment variable **ip** value. 
The line has the format: **ip=string**. Saves the string to data stack and also to the environment under the key **f_name**.
5. `<exp f_name e >` - evaluate the expression **e** and append the string value to file with name **f_name**. 
 Caches the value in environment under the key **f_name**.
6. `<and e1 e2> | e1 <and e2> | e1 e2 <and >` - evaluate expressions **e1** and **e2**. Do logical and and push result to data stack.
7. `<orr e1 e2> | e1 <orr e2> | e1 e2 <orr >` - evaluate expressions **e1** and **e2**. Do logical or and push result to data stack.
8. `<not e1> | e1 <not >` - evaluate expression **e1** and do logical not. Push result to data stack.
9. `<equ e1 e2> | e1 <equ e2> | e1 e2 <equ >` - evaluate expressions **e1** and **e2**. Check if values are equal and push the result to data stack.
10. `<gre e1 e2> | e1 <gre e2> | e1 e2 <gre >` - evaluate expressions **e1** and **e2**. Check if value of **e1** is greater than value of **e2**. 
Push result to data stack.
11. `<les e1 e2> | e1 <les e2> | e1 e2 <les >` - evaluate expressions **e1** and **e2**. Check if value of **e1** is less than value of **e2**. 
Push result to data stack.
12. `<cmd e1> | e1 <cmd >` - evaluate expression **e1** and send the value to router as command. Store the result produced by router in environment 
under the key **output**.
13. `<con e1 e2> | e1 <con e2> | e1 e2 <con >` - evaluate expressions **e1** and **e2**. Do string concatenation and push result to data stack.
14. `<iff e1`  
    `<the e2>`  
    `<els e3>>`
    |  
    `<iff e1`  
    `<the e2>>`  
First evaluates **e1**. If **e1** evaluates to `True`, then evaluatate the line starting with `<the `. If **e1** evaluates to `False`, then evaluate the line starting with `<els `, if provided. **e2** and **e2** cannot span multiple lines. Must be on a single line.
Nested conditionals are supported however mind the number of `>s`. For example: `<set test "good" >`  
                                                                                    `<iff <get test>`  
                                                                                    `<the <iff "True" <the <set t "pass" >>>>>`  
                                                                                    `#>end of <set, >end of inner <the, >end of outer <the`                                                                                     `#>end of inner <iff, >end of outer <iff`  
 All sum up to 5 >. After execution the variable **t** will be set to **pass**.
    
15. `<evl "string" >` - the string enclosed between double/single quotes is evaluated using python's `eval()` function. 
 The result is stored in environment under the key **output**.
If error occurs **output** is set to `""` and the error description is printed.
16. `e1 + e2` - syntactic sugar for `<con >` but more convenient.
17. `e1 and e2` - syntactic sugar for `<and >` but more convenient.
18. `e1 or e2` - syntactic sugar for `<orr >` but more convenient.
19. `e1 != e2` - syntactic sugar for two commands `<equ >` and `<not >` but more convenient.
20. `e1 ge e2` - syntactic sugar for `<gre ` but more convenient.
21. `e1 le e2` - syntactic sugar for `<les >` but more convenient.
22. Lines starting with **#** are ignored and used for comments.
23. Any line that does not start with the special words listed above is send to device as command.

> All logical expressions (6 - 14, 16 - 21) produce boolean results.
