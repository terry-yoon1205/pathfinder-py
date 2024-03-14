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


