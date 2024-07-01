TuGUI
=====

:Author: Davide Manzione, Elena Travaglia
:Contributor: Daniele Tomatis, Gabriele Ottino
:Date: 11/06/2024

.. |space| unicode:: U+00A0
   :trim:

|logo1| |space| |space| |space| |space| |space| |logo2|

.. |logo1| image:: resources/icons/newcleologo.png
   :width: 100
   :alt: newcleo logo

.. |logo2| image:: resources/icons/jrclogo.png
   :width: 100
   :alt: newcleo logo


Introduction
------------

**TuGUI** is a Python-based application intended for providing the
*Transuranus Fuel Performance code*
(`TRANSURANUS <https://data.jrc.ec.europa.eu/collection/transuranus>`_) with
a post-processing GUI.

**TuGUI** allows the user to configure the plot area and select the quantities
to be plotted from those available in the *TRANSURANUS* results file.

*tugui* is developed by the **Codes & Methods** group of
`newcleo <https://www.newcleo.com/>`_ in partnership with the
`JRC-EC <https://commission.europa.eu/about-european-commission/departments-and-executive-agencies/joint-research-centre_en>`_
and it is released under the **GNU Lesser General Public License 3**.

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
- ``tugui``: contains all modules, classes and methods implemented in *tugui*.

*The structure of the repo is currently being defined.*

Dependencies
------------

To run the code, the following dependencies must be satisfied:

- ``Python`` :math:`>= 3.11+`
- ``TtkThemes`` :math:`>= 3.2.2`
- ``Pandas`` :math:`>= 1.5.3`
- ``MatplotLib`` :math:`>= 3.6.3`

To build the documentation in both *html* and *LaTeX* formats, the following
dependencies must be satisfied:

- ``sphinx`` :math:`>= 7.3.7`
- ``sphinx-rtd-theme`` :math:`>= 2.0.0`
- ``myst-parser`` :math:`>= 3.0.1`
- ``sphinxcontrib-bibtex`` :math:`>= 2.5.0`

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

How to Use
----------

To open the GUI, the following command needs to be run from the command prompt:

.. code-block:: bash

    python tugui/main.py

To generate the plots from the results of a *TRANSURANUS* simulation, **TuGUI**
relies on the execution of one of the executables (``TuPlot`` or ``TuStat``,
depending on the case) that extract the *X*-*Y* data for the curves to be
plotted. In particular:

- JRC-EC distributes the Windows-OS version of these executables in the
  ``PostProcessors/TuOutGUI/Exe-Files`` of the *TRANSURANUS* code release;
  please note that such executables may limit some functionalities of
  **TuGUI**, since *batch mode* is not activated;

- the FORTRAN source code of the above executables is provided as well
  in the ``PostProcessors/TuPlot`` and ``PostProcessors/TuStat`` folders,
  correspondingly. Linux users can compile the Linux-OS version of the same
  executables using the ``gfortran`` compiler (*10.+* version). Windows users
  can do the same by using appropriate FORTRAN compiler.

Please note: when compiling both *TuPlot* and *TuStat*, the *batch mode* must
be enabled in the code on both Windows and Linux systems to make **TuGUI**
work properly, that is:

- ``TuPlot``:
   - open ``PostProcessors/TuPlot/TuPlot.f95`` file;
   - comment line 98 ``iMode = 1``;
   - uncomment line 102 ``iMode = 3``.

- ``TuStat``:
   - open ``PostProcessors/TuStat/tustat.f95`` file;
   - comment line 92 ``iMode = 1``;
   - uncomment line 98 ``iMode = 3``.

Once applied these modifications, the user must compile both the executables
and put them into the folder ``tugui/resources/exec`` (to be created) of the
**TuGUI** project.
