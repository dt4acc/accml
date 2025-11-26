# Design choices of accml

When people think about particle accelerators, they often imagine
huge machines flinging particles around at incredible speeds. But
if you look at one from the point of view of the control system
— the place where software and physics shake hands — you find
something much simpler and much more universal: a lot of devices,
each with a handful of numbers you can poke, prod, and read back.

The **accelerator middle layer**, or **accml**, is built around this idea.
It looks at an accelerator — or one of its digital twins — as
nothing more mysterious than a collection of devices whose state
you can update and observe. The trick is to structure the
interaction so that every tool, whether it's a commissioning
script or a simulation engine, can work with the same simple
vocabulary.

This design leans heavily on classic software patterns, on the
idea of *tuple spaces*, and on themes that David Gelernter championed
in *Mirror Worlds*, where he describes systems built by passing small,
structured messages around. It turns out accelerators are a good
fit for that worldview.

## What All These Tools Really Need

When we looked across the existing accelerator tools and workflows,
something interesting became clear: although the tools looked
different on the surface, they all wanted to do more or less the
same three things. Every tool needed to:

* *send transactional-style messages that update the accelerator*,
* *drive sets of actuators through step-by-step sequences* — what
  accelerator physicists usually call a response matrix measurement,
* *or combine both actions*: update some state, measure something,
  update again, and so on.

After each step, the *state* of the accelerator — in the
control-theory sense: a bundle of values describing the system at
that moment — is usually recorded. Often you only need a subset.
Sometimes you want the full picture.

And here’s the important point:
These operations happen not only on the real hardware but also on
*virtual accelerators*, *digital twins*, or full-blown *simulation codes*.
It must be possible to develop and test a sequence of actions on
a simulator and later replay exactly the same sequence on the
real machine. Same script, different destination.

## Why Views Matter

Now, simulation codes don’t think like hardware. They live in a
different coordinate system, a different state space, a different
world entirely. The numbers the hardware deals with might be magnet
currents, RF phases, or vacuum readbacks. The simulation might speak
in terms of lattice functions, normalized coordinates, or
Courant–Snyder parameters.

To keep both worlds straight, accml introduces **views**. The two most
important are:

* the **device view**, which reflects the state the actual hardware
  understands, and
* the **design view**, which reflects the state that simulation tools
  use when computing beam dynamics in the virtual accelerator.

The framework is not limited to these two views — these are simply the
ones the current tools care about most.

## The Update Pattern: Small Messages With Big Consequences

The core interface in accml is built around a simple update
pattern. A command looks like:

```python3
Cmd(dev_id, prop_id, value, behaviour_on_failure)
```
That’s it. One device, one property, one value, and one rule about
what to do if things go wrong. It’s a tiny message, but it has
side effects: it changes the state of the real accelerator, or the
digital twin, or the simulation object it’s applied to.

The beauty of simple messages is that you can send a lot of them,
combine them, replay them, and analyze them. Gelernter would smile
at that.

The details of this pattern — how to represent commands, how to
treat them transactionally, and how they integrate with
digital-twin architectures — are discussed extensively
elsewhere (Khail & Schnizer, 2024; Khail & Schnizer, forthcoming).
Here we focus on how accml uses this pattern in practice.

## Reconciling the Views: Liaison, Translation, and Rewriting

To make device view and design view coexist peacefully, accml
relies on three supporting pillars:

### 1. Liaison management

This is essentially the dictionary that tells us which
`(elem_id, prop_id)` in the design view corresponds to which
`(dev_id, prop_id)` in the device view.

In the usual case this is a one-to-one mapping. But the real world
is never that kind: sometimes a simulated element corresponds to
several physical devices (one-to-many), or several design elements
combine into a single hardware actuator (many-to-one).
Occasionally the matching is many-to-many.

We treat any hidden states the system may have as irrelevant for
this purpose — the same simplifying assumption that underlies a
Markov process without hidden variables.

### 2. Translation service

Once you know which things correspond, you still need to know how
to convert the values. If the design view expresses something in
one coordinate system and the device view in another, the
translation service handles the mathematics. That may mean
converting units, applying coordinate transforms, or computing
derived quantities.

### 3. Command rewriter

Finally, the command rewriter takes a command written in one view
and produces the corresponding command in the other. It rewrites
both the identifiers and the values. This allows exactly the same
high-level work instruction to run on a simulator, a digital twin,
or the real hardware — the system simply rewrites the commands on
the fly.

## Work Instructions: Structured Recipes for the Accelerator

Because commands are small and simple, they can be collected into
sequences — step-by-step recipes. These sequences are what accml
calls *work instructions*.

They are machine-executable yet still human-digestible. A physicist
can read them and understand what the accelerator will do; an
execution engine can run them deterministically.

Khail and Schnizer describe this pattern more fully in their work
on operating digital twins. The key idea is to separate what should
be done from which component actually performs it. The instruction
says what needs to happen; the views and rewriting machinery decide
how to deliver it to the right destination.

## Execution Engines: Orchestrating the Sequence

In architectural terms, a measurement execution engine is the
conductor. It reads the work instructions, dispatches each command
to the appropriate view, rewrites it if necessary, and records the
accelerator state at each step. It doesn’t need to know whether
the underlying system is real hardware, a twin, or a simulation —
the patterns take care of that.

This separation keeps the orchestration logic simple, robust, and
uniform across all destinations.

Further Reading

* David Gelernter’s Mirror Worlds (1991) introduces many of the ideas
  behind message-based architectures and simple state representations.
* For architectural analysis in the accelerator commissioning world,
  see Khail and Schnizer’s work presented at ICALEPCS 2025.
  doi: [10.18429/JACoW-ICALEPCS2025-MOBR002](https://doi.org/10.18429/JACoW-ICALEPCS2025-MOBR002)
* The foundational patterns used in digital twin development are
  detailed in Khail & Schnizer (2024)
   doi: [10.1145/3698322.3698325](https://doi.org/10.1145/3698322.3698325)
  and expanded in their
  forthcoming work on interacting with digital twins
  (W. Sulaiman Khail and P. Schnizer, “Patterns for operating
  and interacting with digital twins”, Lect. Notes Comput. Sci.,
  to be published.).





## Further reading

[1] D. Gelernter, *Mirror Worlds: Or the Day Software Puts the Universe in a Shoebox… How It Will Happen and What It Will Mean*. Oxford University Press, 1991.

[2] W. S. Khail and P. Schnizer, “Accelerator Commissioning Tools: Architectural Proposals and Design Patterns,” in *Proc. ICALEPCS2025*, Chicago, Sep. 2025, pp. 49–55. doi:10.18429/JACoW-ICALEPCS2025-MOBR002.

[3] W. S. Khail and P. Schnizer, “Patterns in Digital Twin Development,” in *Proc. EuroPLoP’24*, New York, NY, USA, 2024. doi:10.1145/3698322.3698325.

[4] W. S. Khail and P. Schnizer, “Patterns for Operating and Interacting with Digital Twins,” *Lecture Notes in Computer Science*, to be published.
