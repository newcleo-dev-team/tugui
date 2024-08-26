=========================
Application configuration
=========================

To install the *tugui* application, please be sure that all the dependencies
are met, and then clone the repository at
https://github.com/newcleo-dev-team/tugui using the following command:

  .. code-block:: bash

    git clone https://github.com/newcleo-dev-team/tugui.


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

Once applied these modifications, the user must compile both the executables,
call them ``tuplotgui`` and ``tustatgui`` respectively,
and put them into the folder ``tugui/resources/exec`` (to be created) of the
**TuGUI** project.