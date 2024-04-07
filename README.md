# pathfinder-py

This is a tool that will attempt to detect unreachable paths in Python code through static program analysis.
In order to determine the satisfiability of branch conditions, it utilizes the Z3 solver to perform symbolic execution of variables.

Currently, the tool only supports a (small) part of the Python language. This includes:
- Pritimitive, numerical variables (i.e. `float`, `int`, `bool`). Other values such as strings, lists, or tuples are not supported.
- Mathematical and boolean operations. Bitwise operations are unsupported.
- If-else conditions.
- While loops.
- For loops with `range()`.
- Calls to user-defined functions which return nothing or a numerical value (as specified above). Calls to any other function will be ignored.

Simple example of a valid input program:
```python
def example(x, y):
    z = x - y
    if z > 0:
        x = x + y
    elif z > 3:
        x = x + y + 3
    else:
        y = 0

    while x > y:
        print(y)
        y = add_two(y)

def add_two(n):
    return n + 2
```
The tool will output that line 6 is unreachable.