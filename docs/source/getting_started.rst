===============
Getting started
===============

This section contains some examples of basic usage of tugui.


Executing the following command from the command prompt

.. code-block:: bash

    python tugui/main.py

the window below will open:

  .. _timevsqin:

  .. figure:: resources/figures/initial_interface.png
    :width: 500
    :align: Center

Plot configuration
==================

The plot-information-file (.pli) of a TRANSURANUS run is the only input required for tugui.

Depending on the value of INSTATI in the simulation input file,
the `TU Plot` or `TU Stat` button will be activated or not.

The micro-file (.mic) and macro-file (.mac) files, produced as output of a TRANSURANUS simulation,
must also be placed in the same folder as the plot-information-file.
Similarly, the statistics files (.sta and .sti) must be placed in the same folder
if you have run a simulation with the statistics module selected.

The working directory is, by default, the one in which the plot-information-file is located.
It is possible to select a different output folder from **File > Set output folder**.
In this directory all plot-files will be stored.

The file TuPlot.inp (or TuStat.inp) containing all the information about the selected plots
is written at the end of the TuPlot (or TuStat) run.


Plot functionalities
====================

The plot window is divided into three sections:

  - The left panel allows the user to select the type of plot they wish to create;

  - The centre panel displays the selected plot;

  - The right panel provides additional information about the selected plot.

It is possible to hide the left and right panes using the buttons located on the left of the main window.

  .. figure:: resources/figures/buttons_for_windows.png
    :width: 500
    :align: Center


Once the initial diagram has been generated, a second diagram can be created
by clicking the button with the plus symbol located on the right-hand side of the main window.
This action will result in the appearance of a new, empty space for the diagram.

  .. figure:: resources/figures/botton_for_new_plot.png
    :width: 500
    :align: Center


Load of a previously-defined plot configuration
===============================================

Upon closing a plot window, a TuPlot.inp (or TuStat.inp) file is automatically generated,
containing all pertinent information regarding the selected plots.
Once a specific input file has been selected,
a previously saved plot configuration can be loaded directly,
thus obviating the necessity for manual replication of all plots.
To accomplish this, simply select the desired .inp file for opening via the
**File > Load > .inp file** option, as illustrated in the figure below.

  .. figure:: resources/figures/load_inp_file.png
    :width: 300
    :align: Center


Direct load of plot curves
==========================

It is possible to load a series of graphics that have already been created directly.
To do so, select **File > Load > .dat/.plt files**.
This will load all .dat files and the corresponding .plt files
that have been previously created via the graphic interface.

  .. figure:: resources/figures/load_dat_files.png
    :width: 300
    :align: Center

GUI menu bar and additional functionalities
===========================================

At the bottom of the central panel is a lower bar which can be used to activate certain functions.
This bar can be used to select the cursor to move the graph and
display only a specific part of the plot.
When this function is activated, the arrows become clickable and
allow you to move through the different views of the graph.
Additionally, the magnifying glass allows you to focus on a specific part of the graph.
To return to the default view instead, use the first button on the bar.

  .. figure:: resources/figures/bottom_bar_move.png
    :width: 300
    :align: Center

Two methods of data storage are available.
The first allows the user to save the plot as a figure,
while the second enables the saving of data as a CSV file.

  .. figure:: resources/figures/bottom_bar_save.png
    :width: 300
    :align: Center

Additionally, the value of a specific point on the graph can be displayed by utilising
the `Cursor on/off` function.
This results in the appearance of a vertical bar within the graph,
with the abscissa and ordinate values corresponding to the point of intersection between the two curves.
By modifying the position of the bar, it is possible to select different points on the graph.


  .. figure:: resources/figures/plot_bar_cursor.png
    :width: 500
    :align: Center

The graph legend can be moved by selecting it directly with the cursor,
and it can also be deactivated by pressing the button as shown in the figure below.

  .. figure:: resources/figures/bottom_bar_legend.png
    :width: 300
    :align: Center