# Check-in 1
Our group has decided to work on an analysis tool for Python.
Current ideas:
- method runtime analysis
- convert loops into list comprehensions
- method call analysis
- type checking for non-statically typed languages (eg. Python)

TA feedback:
- address branching for analysis
- Type checking for Python puts too much work on user 
   - eg. they need to make sure everything is typed
   - dynamic type analysis would be more interesting
- the 2 method analysis can be combined


Our main plan for the time being is just brainstorming ideas for the project, and deciding on an option by late this week/early next week

# Check-in 2

_**(UPDATED) Python Dead code finder**_

After consulting with the TA, we have decided to go with a static Python dead-code checker. It will search for redundant code that do not effect the outcome of a program's execution, as well as unreachable code.

The target demographic is for programmers who want a more sophisticated check on their code for potential dead code that is not caught by a linter or the compiler. 

**Basic Checks**:
- Redundant code

**Control Flow Related Checks**:
- Unreachable code 

The new analysis tool's feature set addresses the concerns presented by the TA that the tool was too simplistic, and did not perform any kind of check or analysis effected by control flow.

_**Division of Responsibilities**_

The team has opted to keep the same teams, as the project shares a similar structure to Project 1 (With parser team doing extractor, and evaluator team doing datalog engine).

_**Roadmap**_


**Week 10 (Check-in 3)**

- Create examples of python code that will trigger each check type.
- Conduct first user study. Incorperate feedback and redo design.
- begin working on tests.

**Week 11 (Check-in 4)**

- finish majority of testing. 
- Conduct final user study. Incorperate feedback.
- have at least a working implementation of checker complete.

**Week 12 (Check-in 5)**

- create video
- finish project and make sure it is bug-free.


# Check-in 3 

**Tool Mockup**

We have created a mockup of our tool's potential output. We used both examples in the user study:

**[Example 1]**

```
def always_true():
    return True

def complex_function(input_value):
    if input_value > 10:
        return "Greater than 10"
    elif input_value == 10:
        if always_true():
            return "Exactly 10"
        print("This line is unreachable due to the return statement above.")
    else:
        if input_value < 5:
            return "Less than 5"
        elif input_value < 3:
            return "Less than 3"

    try:
        if always_true() == False:
            raise ValueError("Random failure occurred")
        print("If an exception is thrown, this line won't be reached.")
    except ValueError as e:
        print(f"Caught an exception: {e}")
        return "Exception handled"

    return "Normal execution path"
```

tool output:

- Unreachable Code Detected:
(Location: Line 12)
Issue: Print statement "This line is unreachable due to the return statement above." is never executed because it follows a return statement within the same conditional block.

- Logic Flaw Detected:
(Location: Line 16)
Issue: Conditional branch "elif input_value < 3:" is logically unreachable. Given the preceding condition "if input_value < 5:", this branch will never be executed, as any value less than 3 would have already satisfied the previous condition and exited the function.

- Conditional Reachability:
(Location: Line 22)
Issue: Print statement "If an exception is thrown, this line won't be reached." is conditionally unreachable since the exception is always throw

**[Example 2]**

![image](https://media.github.students.cs.ubc.ca/user/4234/files/98c01db0-1a8d-4a99-aeb3-03bf3a8a3771)

tool output:

- Unused Function Detected:
Name: unused_function
Description: This function is defined but never used anywhere in the code.
(Line: 16)

- Unused Class Detected:
Name: UnusedClass
Description: This class is defined but never instantiated or used.
(Line: 19)

- Unused Function Detected:
Name: cleanup_data
Description: This function is defined but not called anywhere in the code.
(Line: 9)

- Unused Class Detected:
Name: DataAnalyzer
Description: This class and its method 'analyze' are defined but not used.
(Line: 12)

- Unused Variable Detected:
Name: UNUSED_SETTING
Description: This variable is assigned a value but not used in the code.
(Line: 1)


**User Study 1**

Here is the feedback we recieved from the user:

-> Providing so much detail on these trivial issues in the report is maybe not needed
  -> Simplify error report by concatenating errors:
      e.g.)
      
      (OLD)
      unreachable code on line 15
      unreachable code on line 46

      vs.

      (NEW)
      unreachable code on line 15, 46
      
-> tool is redundant for small snippets of trivial code, can be done quickly by user. If that is the case, the main use case is probably to quickly clean up a giant codebase where a user would not want to do manually. 

-> In that case, I would like way to auto-implement all changes like in a github conflict resolver UI

-> add ways to blacklist lines that are just stubs, or limit analysis to certain files only

-> would be nice to have a visual component showing the code vs. refactored code, with the removed areas highlighted

**Timeline**

We have completed everything as planned for check-in 3 except begin writing tests. We will get on that as soon as possible.
