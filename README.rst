TUGUI
=====

.. image:: resources/icons/newcleologo_hd.png
   :width: 100
   :alt: newcleo logo

:Author: Davide Manzione, Elena Travaglia
:Contributor: Daniele Tomatis, Gabriele Ottino
:Date: 30/08/2024

Introduction
------------

**TUGUI** is a Python-based application intended for providing the
*Transuranus Fuel Performance code*
(`TRANSURANUS <https://data.jrc.ec.europa.eu/collection/transuranus>`_) with
a post-processing GUI.

**TUGUI** allows the user to configure the plot area and select the quantities
to be plotted from those available in the *TRANSURANUS* results file.

**TUGUI** is developed by the **Codes & Methods** group of
`*new*\cleo <https://www.newcleo.com/>`_ and it is released under the
**BSD 3-Clause License**.

**DISCLAIMER:** **TUGUI** project must not contain any confidential or
proprietary content of *TRANSURANUS*. The user must address a license request
for the **Transuranus Software Package (Version v1m1j24)** to
`JRC-EC <https://commission.europa.eu/about-european-commission/departments-and-executive-agencies/joint-research-centre_en>`_.
**Transuranus Software Package** is not distributed with **TUGUI**.

Project Structure
-----------------

The project is organized according to the following folder structure:

.. code:: text

  <tugui parent folder>
    ├── docs/
    ├── resources/
    ├── tests/
    ├── tugui/
    ├── LICENSE
    └── README.rst


- ``docs``: contains files for the generation of the documentation by Sphinx;
- ``resources``: contains files that support the configuration and operation of the GUI;
- ``tests``: contains input files needed for test purposes;
- ``tugui``: contains all modules, classes and methods implemented in **TUGUI**.

Dependencies
------------

To run the code, the following dependencies must be satisfied:

- ``Python`` :math:`>= 3.11+`
- ``sv-ttk`` :math:`>= 2.6.0`
- ``Pandas`` :math:`>= 2.2.2`
- ``MatplotLib`` :math:`>= 3.9.0`
- ``Typing-extensions`` :math:`>= 4.12.2`

To build the documentation in both *html* and *LaTeX* formats, the following
dependencies must be satisfied:

- ``sphinx`` :math:`>= 7.3.7`
- ``sphinx-rtd-theme`` :math:`>= 2.0.0`
- ``myst-parser`` :math:`>= 3.0.1`
- ``sphinxcontrib-bibtex`` :math:`>= 2.6.2`

How to Install
--------------

To install the **TUGUI** application, please check that all the dependencies
are met, and then clone the repository at
https://github.com/newcleo-dev-team/tugui using the following command:

  .. code-block:: bash
    
    git clone https://github.com/newcleo-dev-team/tugui.

How to Use
----------

To open the GUI, run the following command from the command prompt:

  .. code-block:: bash

    python tugui/main.py

To generate the plots from the results of a *TRANSURANUS* simulation, **TUGUI**
relies on the execution of one of the executables (``TuPlot`` or ``TuStat``,
depending on the case) that extract the *X*-*Y* data for the curves to be
plotted. In particular:

- JRC-EC distributes the Windows-OS version of these executables in the
  ``PostProcessors/TuOutGUI/Exe-Files`` of the *Transuranus Software Package*;
  please note that such executables may limit some functionalities of
  **TUGUI**, since *batch mode* is disabled;

- the FORTRAN source code of the above executables is provided as well
  in the ``PostProcessors/TuPlot`` and ``PostProcessors/TuStat`` folders,
  correspondingly. Linux users can compile the Linux-OS version of the same
  executables using the ``gfortran`` compiler (*10.+* version). Windows users
  can do the same by using appropriate FORTRAN compiler. We recommend
  *Silverfrost FTN95* as FORTRAN compiler on Windows Operative Systems.


**Please note**: when compiling both *TuPlot* and *TuStat*, the *batch mode*
must be enabled in the code on both Windows and Linux systems to make **TUGUI**
work properly. Please, refer to chapters **15.4** and **16.4.5**,
respectively, of **TRANSURANUS HANDBOOK** that is distributed within the
*Transuranus Software Package*.

Once applied these modifications, the user must compile both executables,
call them ``tuplotgui`` and ``tustatgui`` respectively, 
and put them into the folder ``tugui/resources/exec`` (to be created) of the
**TUGUI** project.

Documentation
-------------

The Sphinx documentation can be built in *html* and *LaTeX* formats by
executing the following command in the folder ``docs/``:

  .. code-block:: bash

      make html

  .. code-block:: bash

      make latexpdf

To see the available templates for generating the documentation in *PDF*
format and to choose among them, please look at the ``docs/conf.py`` file.

How to Contribute
-----------------

For anyone wishing to contribute to the development of the project, report
issues or problems with the software, or request support, please refer to this
`web page <https://github.com/newcleo-dev-team/tugui/blob/master/CONTRIBUTIONS.rst>`_.

Developers issuing pull requests for consideration and acceptance of their
work into the main development branch of **TUGUI** must first verify that no
original content of the *Transuranus Software Package* is contained in their
own development.

Acknowledgement
---------------

*new*\cleo is thankful to the *TRANSURANUS* development team of
`JRC-EC Karlsruhe <https://commission.europa.eu/about-european-commission/departments-and-executive-agencies/joint-research-centre_en>`_
for distributing their software to *new*\cleo and for supporting the
development of **TUGUI**.