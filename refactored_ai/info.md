# Info

This AI should behave identically to stable_ai and give the same results for the same board.

It should only be refactored for better readability and to make it more efficient.

Always test that it indeed gives the same results as stable_ai.


\refactored_ai\ai_0.py 

h8h7 has 2018 Beta cutoffs

Leaf nodes: 113496 extensions: 16254 maximum depth:12

[1, 43, 252, 1312, 8457, 16716, 22594, 28883, 34257, 5322, 7782, 225, 4, 0, 0, 0, 0, 0, 0, 0]

first move last: [-4.0, -1.0, -3.0, 0, 'e1g1', 'a8c8', 'd3c3']

Move # 19: d3c3. [Sum, Pos., ..., ..., Path... ] - 2023-11-15 18:39:30

Execution time: 17726 milliseconds


--------------
Somehow it is not identical but I don't know where
Really really close though

Leaf nodes: 113496 extensions: 16254 maximum depth:12

[1, 43, 251, 1311, 8423, 16714, 22594, 28884, 34257, 5322, 7782, 225, 4, 0, 0, 0, 0, 0, 0, 0]
first move last: [-4.0, -1.0, -3.0, 0, 'e1g1', 'a8c8', 'd3c3']

Move # 19: d3c3. [Sum, Pos., ..., ..., Path... ] - 2023-11-15 19:25:11

Execution time: 17641 milliseconds


[295, 687, 6030, 3602, 1416, 471, 0, 0, 2461]

stable:

[294, 686, 6030, 3599, 1416, 471, 0, 0, 2460]