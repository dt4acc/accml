# Design choices of accml

## General design choices

The design of `accml` is based on specific software design 
patterns next to the concept of a *tuple space*  or the 
outlines given by David Gelernter's *Mirror Worlds* [1].

`accml` focuses on interacting with an *accelerator* or an 
*accelerator* complex, its equivalent twins or simulation
complex. Furthermore, its interacts with this complex based
on *simple structured messages* (for further details see [2]) 

These choices were made  based on the  analysis of available
requirements. These showed that all different tools actually 
need:

* update the accelerator with a transactional style update
* have a set of actuators that need to be driven to a sequence
  of values step by step: this is often referred to as 
  response matrix measurement
* or combine these two steps

Typically, the state of the accelerator is recorded after each step.
Often  a subset of this state is sufficient.

Furthermore, it was noted that these steps are executed on the 
accelerator itself, its virtual representation or on simulation tools.
Therefore, the same command needs to be sent to different destinations. 
Sometimes it is necessary to build up and test a set of commands
on e.g. a simulator or twin and then to replay these commands 
to the real machine.

  
The second major point is that simulation tools use a 
largely different coordinate system or state space than 
simulation tools. We call these different states or 
coordinate systems *different views* of the 
same system.

These design choices are different to other tools: `accml` sees
an accelerator as a *complex* that consists of a set of *devices*. 
Its focus is on the accelerator itself. It provides an interface
using the *device names* as these are typically known to the user.
These are valid within their view.

The last pillar are concepts of *work instructions*. As will be 
shown later, the patterns allow representing the interaction with
the real machine, it digital twin or simulation tools in a manner 
which separates *what* shall be done nicely from *which components 
need to execute it*.


## Patterns used 

### update pattern

Core interface is the update pattern provided by 
*todo* xxx facade. Its interface is 

```python3

f.update(dev_id: str, prop_id: str, value: object, on_error)
```

We call these parameters a command. This command is only valid
within its associated *view*. This pattern is described in detail in [3].

This command is with side effects: it changes the state of the 
accelerator or its digital twin or its simulation object. 

### Combining the views

Currently, two views are considered: the device view which represents the 
state that the accelerator devices use and the design view which represents
the state that the simulation tools use that perform the calculations for the 
virtual accelerator or its twin.

As the simulation codes use a very different state than the real world devices,
it is necessary to convert between these two. This is based on the following 
aspects:

* liaison management: which *(elem_id, prop_id)* of the design view match 
  which *(dev_id, prop_id)* of the device view. Please note that dev_id 
  is named elem_id in the design view, as one refers to the simulations 
  building blocks as elements.

* translation service: provides calculation objects that convert the value

* command rewriter: uses liaison managerment and translation service to 
  rewrite commands valid in one view to the other.

The split up of the patterns 
These patterns and their advantages are discussed in detail in [4]. 
Liasion managment and translation service split between:

* who needs to communicate to whom
* how does their input be changed so that the other side can understand them.

  
## Implementing computer understandable *work instructions*

The description above described how state is changed inside the 
accelerator next on how the views are combined.

It was shown that the communcation to the underlaying system happens
using small simple commands. These commands can be combined in a
sequence. This set of commands then form a work instruction.
A *measurement execution engine* then takes care executing these 
commands. Further details are given in [4].



## Further reading

[1] D. Gelernter, *Mirror Worlds: Or the Day Software Puts the Universe in a Shoebox… How It Will Happen and What It Will Mean*. Oxford University Press, 1991.

[2] W. S. Khail and P. Schnizer, “Accelerator Commissioning Tools: Architectural Proposals and Design Patterns,” in *Proc. ICALEPCS2025*, Chicago, Sep. 2025, pp. 49–55. doi:10.18429/JACoW-ICALEPCS2025-MOBR002.

[3] W. S. Khail and P. Schnizer, “Patterns in Digital Twin Development,” in *Proc. EuroPLoP’24*, New York, NY, USA, 2024. doi:10.1145/3698322.3698325.

[4] W. S. Khail and P. Schnizer, “Patterns for Operating and Interacting with Digital Twins,” *Lecture Notes in Computer Science*, to be published.


