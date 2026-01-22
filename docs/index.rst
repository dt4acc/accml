accml documentation
===================


.. toctree::
   :caption: Contents
   :maxdepth: 1
   :glob:

   background/design.rst
   background/implementation.rst
   api/accml.rst


Introduction
------------

accml provides a particle accelerator middle layer, which is built using
a clean architecture and structured communication. It consists of two
main packages: `accml` it self and the libray `accml_lib`.

* accml_lib contains:

    * used data models
    * interface definitions
    * and all code which is used by client and twin code

* accml contains:
    * code that is only used by the client

The `accml` design is described in :doc:`background/design`.
Its implementation concepts are give in
:doc:`background/implementation`.


Installation
============

``pip`` support will be provided later. For the time being, follow these steps.

First clone the repository:

.. code-block:: bash

    git clone https://github.com/python-accelerator-middle-layer/accml.git --recurse-submodules

Create a fresh virtual environment (the name ``venv-accml`` is just an example):

.. code-block:: bash

    python3 -m venv venv-accml

Activate the virtual environment. In a Bourne-style shell (e.g. ``bash``) run:

.. code-block:: bash

    source venv-accml/bin/activate

Now install ``accml`` in the activated environment.

For an EPICS facility use:

.. code-block:: bash

    python3 -m pip install \
        'accml[bluesky-epics]' accml \
        'accml/external-repositories/accml_lib[bluesky-epics,pyat-simulator]'

For a TANGO facility use:

.. code-block:: bash

    python3 -m pip install \
        'accml[bluesky-tango]' accml \
        'accml/external-repositories/accml_lib[bluesky-tango,pyat-simulator]'



Getting started
---------------

Have a look to the example directory of accml! Please drop a line for any
further information.

API documentation
-----------------

* accml documentation :doc:src/accml.rst
* accml_lib documentation at  https://python-accelerator-middle-layer.github.io/accml_lib/src/accml_lib.core.html

Collaboration community
-----------------------

Discussion
~~~~~~~~~~

`Mattermost <https://mattermost.hzdr.de/accelerator-middle-layer/channels/town-square>`_

(please log in using Helmoltz ID, you will be prompt to access with your own lab/university credentials)

Shared documents
~~~~~~~~~~~~~~~~

to access the shared documents please ask S.Liuzzo for access rigths. 

The  "software requirement specification" document is visible here:
https://www.overleaf.com/project/67d2b7d267244c3902da8265


Mailing list:
~~~~~~~~~~~~~
to be added to the pyAML mailing list please write to S.Liuzzo



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

