TuGUI
=====

:Author: Davide Manzione, Elena Travaglia, Daniele Tomatis
:Contributor: 
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
    