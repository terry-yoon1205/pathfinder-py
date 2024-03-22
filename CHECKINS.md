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

_**(UPDATED) Python Unreachable Path Analyzer**_

This tool will perform static analysis on Python code, attempting to detect branches that will never be traversed. By detecting unreachable paths, the tool will aid Python developers in cleaning up snippets of code that are unnecessary. In cases where the detected unreachable paths are supposed to be reachable (i.e. the result is unexpected), it will help in finding and resolving bugs in the code.

This tool's results will be an optimistic over-approximation, as it may not always detect unreachable paths that are present. This is because we want to make sure any bugs or deletable code that we signal as existent is real, and not waste anyone's time with false positives.

This new analysis tool addresses the concerns presented by the TA that the tool was too simplistic and was rather concerned with meta-property analysis, and did not perform checks on properties affected by control flow.

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

*UPDATE*:
Since the first user study, we have determined that finding unused variables/classes/functions is too simple and not particularly related to the purpose of the analysis - we will instead focus on detecting unreachable branches. We have also realized that the tool outputs that we presented to the users were too complex and not realistic to achieve using a code analyzer. We will aim to only provide the line numbers or ranges of numbers that are unreachable.

# Check-in 4
**Status of implementation:**

Everyone is writing their tests and implementations

**Final user study:**

We’re planning to do the user study with revisioned examples from previous user study and some new examples

_**Revised Timeline:**_

**Week 12 (Check-in 5)**
- final user study
- finish majority of implementation

**Week 13**
- finish project
- make video
