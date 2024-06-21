TuGUI
=====

:Author: Davide Manzione, Elena Travaglia, Daniele Tomatis
:Contributor: 
:Date: 11/06/2024

.. image:: resources/icons/newcleologo.png
  :width: 50%
  :alt: newcleo logo
.. image:: resources/icons/jrclogo.png
  :width: 50%
  :alt: JRC logo

Introduction
------------

**TuGUI** is a Python-based application intended for providing the *Transuranus Fuel Performance code*
(`TRANSURANUS <https://data.jrc.ec.europa.eu/collection/transuranus>`_) with a post-processing GUI.

**TuGUI** allows the user to configure the plot area and select the quantities to be plotted from those
available in the *TRANSURANUS* results file.

*tugui* is developed by the **Codes & Methods** group of `newcleo <https://www.newcleo.com/>`_ in partnership with the
`JRC-EC <https://commission.europa.eu/about-european-commission/departments-and-executive-agencies/joint-research-centre_en>`_
and it is released under the **GNU Lesser General Public License 3**.

Project Structure
-----------------

The project is organized according to the following folder structure:

.. code:: text

  <tugui parent folder>
    ├── resources/
    ├── tests/
    ├── tugui/
    ├── LICENSE
    └── README.rst

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
- ``MatplotLib`` :math:`>=3.6.3`

How to Use
----------

To open the GUI, the following command needs to be run from the command prompt:

.. code-block:: bash

    python tugui/main.py
    