The Design of ``accml`` and ``accml_lib``
=======================================

Let us begin by forgetting software for a moment and asking a very
simple question:

What are we actually trying to do?

We want to run a particle accelerator well. That means we want to
change machine settings, observe what the machine does, compare this
behavior with what we expected, and learn how the machine responds
when we change something.

Everything else — simulations, controls software, data storage —
exists only to serve that purpose.

The overall concept of how users interact with such a system, and how
simulation and machine operation are unified from a user perspective,
is described in detail in :cite:`twin-architecture:icaleps2025`.

One Machine, Many Descriptions
------------------------------

There is only one physical accelerator, but there are many ways to
describe it.

A simulation describes the accelerator in terms of an ideal lattice,
ideal particles, and deviations from a reference orbit. The real
machine, however, consists of magnets, power converters, cavities, RF
amplifiers, and real particles moving through real hardware.

Both descriptions refer to the same machine, but they look at it from
different angles. We call these angles *views*.

A view is a coordinate system, a set of building blocks, and a
conceptual abstraction of the machine. The simulation view and the
machine view are peers: neither is authoritative. Together they form a
*digital twin*.

This peer relationship of views and their role in forming a digital
twin is a central idea of the architecture presented in
:cite:`twin-architecture:icaleps2025`.

Relative Thinking and Exploration
---------------------------------

In daily operation and studies, we rarely ask for absolute values. We
ask how the machine behaves relative to some reference.

That reference may be the design working point, a previously saved
setup, or the current machine state. What matters is the difference
between prediction and observation.

This is very similar to controller design: the focus is on forecasting
changes and analysing deviations. These differences — the *gap*
between expectation and reality — are where understanding is gained.

Building Blocks and Identification
----------------------------------

Every piece of information exchanged between views must clearly state
two things: what object it refers to, and which property of that object
is meant.

We therefore identify information by:
- a *building block identifier*, and
- a *property identifier*.

In the design view, building blocks correspond to lattice elements. In
the real machine view, they correspond to physical or logical devices
such as magnets, power converters, cavities, or RF systems. A building
block should be understood as a real-world object or its digital
representation.

The Liaison Manager
-------------------

In large collaborations, problems are not solved by contacting
everyone. Instead, liaison managers connect the right people.

The same idea is applied here. A *liaison manager* is a concrete
software component that knows which building blocks correspond across
views. It does not perform translations or physics calculations; it
simply knows who should talk to whom.

This pattern, together with other architectural patterns used in
``accml``, is described in detail in :cite:`dt:europlop25`.

Translation Between Views
------------------------

Even when corresponding building blocks are known, they often do not
use the same language.

One view may use different units, scaling, or coordinate systems than
another. In many cases the translation is simple, but in others it
resembles a full coordinate transformation.

Translations are handled by dedicated translation objects. The
translation service itself only selects the appropriate translator;
the details are encapsulated elsewhere.

This separation of concerns is part of the translation service pattern
described in :cite:`dt:europlop25`.

Structured Communication: Commands
----------------------------------

Interaction with either the digital twin or the real accelerator is
based on immutable command messages.

The simplest command is a read command:

.. code-block:: python

   ReadCommand(id="quad", property="set_current")

This expresses the request to read a property of a building block.

To change a value, a command with a value is used:

.. code-block:: python

   Command(
       id="quad",
       property="set_current",
       value="245",
       behaviour_on_error=None
   )

Commands are handed to dedicated execution engines; they do not execute
themselves.

From Commands to Measurements
-----------------------------

From individual commands, more complex structures are built:

- *transaction commands*, which are executed together,
- *command sequences*, which are executed step by step.

A command execution engine manages ordering, timing, routing, and
error handling.

A *measurement execution engine* extends this concept by delegating
produced data to a storage system. Conceptually, it is a command
execution engine combined with persistence handling. This pattern is
also described in :cite:`dt:europlop25`.

The Role of ``accml_lib``
------------------------

``accml_lib`` contains the shared abstractions and mechanisms used by
both the digital twin implementation and client applications.

Client applications use the same commands and concepts whether they
interact with the digital twin or the real accelerator. The difference
lies only in the backend.

The software architecture and separation of concerns from a software
engineering perspective are discussed in :cite:`dt:deRSE25`.

Implementation and Updates
--------------------------

An update on an actual digital twin implementation based on these
concepts, including operational experience, is presented in
:cite:`dt4acc:ipac25`.

Further Reading
---------------

Setting up a digital twin, switching its modes, and transitioning
between simulation and machine operation are discussed in
:cite:`dt:europlop24`.

This provides additional background beyond the core architectural
concepts described here.




.. rubric:: References

.. bibliography:: refs.bib
   :style: unsrt