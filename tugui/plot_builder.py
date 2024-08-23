import csv
from typing import Literal
import numpy as np
import os
import pandas as pd
import re
import tkinter as tk

from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.backends import _backend_tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.offsetbox import AnnotationBbox, TextArea, VPacker
from numpy.typing import ArrayLike
from tkinter import ttk
from tkinter.filedialog import asksaveasfilename
from typing import Callable, Dict, List, Union, Tuple


class PlotFigure(ttk.Frame):
  """
  Class that provides a frame for displaying the results in terms of a plot window
  and one showing the corresponding report produced by running the TU plot
  executables.
  It inherits from the ttk.Frame class and builds the content within a PanedWindow
  object in terms of:
    . plot: a Frame object describing the plot area made of a Figure and a
      CustomToolbar instance;
    . report: a Frame object providing a Text object for the report to display.
  """
  def __init__(self, container: tk.Misc) -> None:
    super().__init__(container)

    # Build a paned window
    panedwindow = ttk.PanedWindow(self, orient='horizontal')
    panedwindow.grid(column=0, row=0, sticky='nsew')
    # Build a frame holding the plot
    plot_frame = ttk.Frame(container)
    plot_frame.grid(column=0, row=0, sticky='nsew')
    # Configure the plot frame rows and column
    plot_frame.grid_rowconfigure(0, weight=3)
    plot_frame.grid_rowconfigure(1, weight=0)
    plot_frame.grid_columnconfigure(0, weight=3)
    # Build a frame holding the plot report text
    self.report_frame: ttk.Frame = ttk.Frame(container)
    self.report_frame.grid(column=0, row=0, sticky='nsew')
    # Build the content of the report frame
    self._build_report_area(self.report_frame)

    # Add the two frames to the panedwindow specifying how each one should expand
    # if the container is resized ('weight' option).
    panedwindow.add(plot_frame, weight=3)
    panedwindow.add(self.report_frame, weight=1)

    # Instantiate the figure that will contain the plot; it is treated as an instance attribute
    self.fig: Figure = Figure(figsize = (10, 5), dpi = 100)
    self.fig.add_subplot(111)
    # Add a Tkinter canvas within the plot frame and that holds the matplotlib Figure object
    canvas = FigureCanvasTkAgg(self.fig, master = plot_frame)
    canvas.draw()
    # Place the canvas into the Frame grid, by specifying to expand in all directions
    canvas.get_tk_widget().grid(column=0, row=0, sticky='nsew')

    # Instantiate the toolbar
    self.toolbar: CustomToolbar = CustomToolbar(canvas, plot_frame, False)
    # Reset the axes
    self.toolbar.update()
    # Place the toolbar into the Frame grid
    self.toolbar.grid(column=0, row=1)

    # Configure this instance frame in terms of its rows and column
    self.grid_rowconfigure(0, weight=3)
    self.grid_rowconfigure(1, weight=0)
    self.grid_columnconfigure(0, weight=3)

    # Bind the deselection of the toolbar buttons to the "DeselectButtons" event
    self.bind('<<DeselectButtons>>', func=lambda event: self.toolbar.reset_toolbar_buttons())

  def _build_report_area(self, report_frame: ttk.Frame) -> None:
    """
    Method that builds the report area (as a Text widget) where the content of the
    .out file is displayed.
    """
    # Create an horizontal scrollbar for the text area
    hscrollbar = ttk.Scrollbar(report_frame, orient='horizontal')
    hscrollbar.pack(fill='x', side='bottom')
    # Create a vertical scrollbar for the text area
    vscrollbar = ttk.Scrollbar(report_frame, orient='vertical')
    vscrollbar.pack(fill='y', side='right')

    # Instantiate a Text widget that displays the content of the .out file
    self.text_widget = tk.Text(report_frame, wrap='none', width=10, exportselection=False)
    self.text_widget.pack(fill='both', side='left', expand=True)
    # Set the default state as disabled
    self.text_widget.configure(state=tk.DISABLED)

    # Configure the both horizontal and vertical scrollbars
    hscrollbar.configure(command=self.text_widget.xview)
    vscrollbar.configure(command=self.text_widget.yview)
    # Configure the text area with the scrollbars
    self.text_widget.configure(xscrollcommand=hscrollbar.set)
    self.text_widget.configure(yscrollcommand=vscrollbar.set)

    # Bind 'Ctrl+A' to the selection of all the content of the Text widget
    self.text_widget.bind("<Control-Key-a>", self._select_all_report)
    self.text_widget.bind("<Control-Key-A>", self._select_all_report) # In case caps lock is on
    # Bind 'Ctrl+C' to the copy action for the currently selected text in the Text widget
    self.text_widget.bind("<Control-Key-c>", self._copy_report_selection)
    self.text_widget.bind("<Control-Key-C>", self._copy_report_selection) # In case caps lock is on

  def _select_all_report(self, event: tk.Event) -> str:
    """
    Method that selects all the content of the text widget showing the plot report.
    """
    # Apply the 'SEL' tag (indicating the selected text) to all text from start to end
    self.text_widget.tag_add(tk.SEL, "1.0", tk.END)
    # Set the 'INSERT' mark at the start of the text box
    self.text_widget.mark_set(tk.INSERT, "1.0")
    # Adjusts the window view so to make the text at the cursor position visible
    self.text_widget.see(tk.INSERT)
    # Stops other bindings on this event from being invoked
    return 'break'

  def _copy_report_selection(self, event: tk.Event) -> None:
    """
    Method that copies the current report selection to the clipboard.
    """
    # Check if there is currently any text selected
    if self.text_widget.tag_ranges(tk.SEL):
      # # Get the selected text
      selected_text = self.text_widget.get(tk.SEL_FIRST, tk.SEL_LAST)
      # Add the selected text to a DataFrame object
      df = pd.DataFrame([selected_text])
      # Use the pandas clipboard functionality to copy the text to the clipboard
      df.to_clipboard(index=False, header=False)


class CustomToolbar(NavigationToolbar2Tk):
  """
  Class that provides a customization of the default toolbar provided by the matplotlib
  library as the 'NavigationToolbar2Tk' object.
  This class inherits from the 'NavigationToolbar2Tk' class and adds additional buttons
  for enabling the following functionalities:
    . cursor: activation of a cursor that shows the X-Y data of the currently active curves
    . legend: deactivation of the plot legend
    . save as CSV: functionality for saving the X-Y data of the currently active curves
      to a file in the CSV format.
  """
  def __init__(self, canvas: tk.Canvas, frame: tk.Frame,
               pack_toolbar: bool = False, axes: Union[Axes, None] =None,
               x: List[ArrayLike] = None,
               ys: List[ArrayLike] = None) -> None:
    super().__init__(canvas, window=frame, pack_toolbar=pack_toolbar)

    # Add the cursor button to the toolbar
    self._add_new_button(name='cursor',
                         text='Cursor On/Off',
                         img_relpath='../resources/icons/plotcursor.png',
                         toggle=True,
                         command=self.need_cursor_activation,
                         tooltip='Cursor On/Off')
    # Add the legend button to the toolbar
    self._add_new_button(name='legend',
                         text='Legend On/Off',
                         img_relpath='../resources/icons/hidelegend.png',
                         toggle=True,
                         command=self.need_legend_activation,
                         tooltip='Legend On/Off')
   # Add the save CSV button to the toolbar
    self._add_new_button(name='savecsv',
                         text='Save CSV',
                         img_relpath='../resources/icons/savecsv.png',
                         toggle=False,
                         command=self.save_csv,
                         tooltip='Save data as CSV')
    # Disable the toolbar buttons in case no Axes object has been provided
    if not axes:
      self.get_toolbar_button('cursor').configure(state='disabled')
      self.get_toolbar_button('legend').configure(state='disabled')
      self.get_toolbar_button('savecsv').configure(state='disabled')

    # Set the initial directory
    self.initial_dir: str = os.getcwd()

    # Instantiate the PlotCursor class
    self.cursor: PlotCursor = PlotCursor(axes, x, ys)

  def get_toolbar_button(self, button_name: str) -> Union[tk.Button, tk.Checkbutton]:
    """
    Method that, given a string representing the toolbar button name, it returns
    the corresponding button, either as an instance of the 'tk.Button' or the
    'tk.Checkbutton' class.
    """
    return self._buttons[button_name]

  def need_cursor_activation(self) -> None:
    """
    Method that is called when the cursor button is pressed. Depending on the PlotCursor
    object 'button_state' attribute, the corresponding method of the PlotCursor instance
    is called to handle the activation/deactivation of the cursor widget.
    """
    print("Activate cursor?", not self.cursor.button_state)
    # Check the cursor button 'state' attribute
    if self.cursor.button_state:
      ###################################################################
      # The cursor button is currently on, hence it has to be deactivated
      ###################################################################
      # Set the cursor instance variable, storing the corresponding button state, to False
      self.cursor.set_button_state(False)
      # Call the cursor object method for handling the cursor deactivation
      self.cursor.deactivate_cursor()
    else:
      ##################################################################
      # The cursor button is currently off, hence it has to be activated
      ##################################################################
      # Set the cursor instance variable, storing the corresponding button state, to True
      self.cursor.set_button_state(True)
      # Call the cursor object method for handling the cursor activation
      self.cursor.activate_cursor()

  def need_legend_activation(self) -> None:
    """
    Method that is called when the legend button is pressed. Depending on the
    legend current visibility, the opposite state is assigned.
    """
    # Return immediately if no Axes object is present in the instance
    if not hasattr(self, 'axes'): return
    print("Legend visibility", self.axes.get_legend().get_visible())
    # Check the legend 'visibilty' attribute
    if self.axes.get_legend().get_visible():
      print("Switching legend off...")
      # The legend is currently on, hence it has to be deactivated
      self.axes.get_legend().set_visible(False)
      # Disable mouse dragging support for the legend
      self.axes.get_legend().set_draggable(False)
    else:
      print("Switching legend on...")
      # The legend is currently off, hence it has to be activated
      self.axes.get_legend().set_visible(True)
      # Activate mouse dragging support for the legend
      self.axes.get_legend().set_draggable(True)

    # Re-draw the figure
    self.axes.figure.canvas.draw_idle()

  def reset_toolbar_buttons(self) -> None:
    """
    Method that resets the additional buttons of the toolbar. In particular, both the
    cursor and the legend buttons are toggled off, while the PlotCursor related instance
    attributes are set to False.
    """
    # Toggle off the toolbar buttons
    self.get_toolbar_button('cursor').deselect()
    self.get_toolbar_button('legend').deselect()
    # Set the corresponding PlotCursor instance attributes to False
    self.cursor.state = False
    self.cursor.set_button_state(False)

  def save_csv(self) -> None:
    """
    Method that enables the functionality for saving the X-Y data of the currently
    active curves on a file in CSV format. In case the plot presents curves with
    different X-values (as identified by the PlotCursor object 'display_mode'
    attribute), a CSV file for each curve is produced with the corresponding X-Y
    values.
    """
    if not hasattr(self, 'active_curves'):
      raise Exception("No save action can be performed as no curves are currently present.")
    # Define the file types to save to
    files = [('CSV Files', '*.csv*')]
    # Pop-up a window for allowing the user to select the file name and the output folder
    filename = asksaveasfilename(confirmoverwrite=True,
                                 defaultextension='.csv',
                                 filetypes=files,
                                 initialdir=self.initial_dir)

    # Extract two lists holding the curves handles (i.e. the Line2D objects) and the legend respectively
    handles, legends = self.axes.get_legend_handles_labels()
    # Intersect the plot handles/legends lists with the list of currently active curves and build a dictionary
    curves_to_save = dict()
    curves_to_save.update({h: l for h, l in zip(handles, legends) for c in self.active_curves if c == h})

    # Get the list of X-data for each of the active curves
    curves: List[Line2D] = list(curves_to_save.keys())
    # Define the header list with elements being the legend labels
    headers = list(curves_to_save.values())
    # Add the plot X-axis label in the first position of the header list
    headers.insert(0, self.axes.get_xaxis().get_label_text())

    # Get the display mode of the cursor to understand how the CSV file should be produced:
    # . 'X-Y': curves have different X values, hence one file for each curve is saved;
    # . 'YYX': curves have the same X values, hence one file is saved;
    if self.cursor.display_mode == 'X-Y':
      # Declare a plot index
      indx = 1
      # Loop over all the active curves
      for curve in curves:
        # Split the file and the extension
        (path, extension) = os.path.splitext(filename)
        # Add the plot index to the file name choosen by the user
        filename_i = path + '_' + str(indx) + extension

        # Open the CSV file for writing the content
        with open(file=filename_i, mode='w') as csv_file:
          # Declare a writer object responsible for converting the user data into a string to write on a line
          writer = csv.writer(csv_file)
          # Write the header on the first line
          writer.writerow([headers[0], headers[indx]])

          # Get the X-Y lists of the current curve
          x = curve.get_data()[0]
          y = curve.get_data()[1]

          # Loop over all the X-values
          for i in range(0, len(x)):
            # Write the single line made of the i-th X-Y values in the CSV file
            writer.writerow([x[i], y[i]])
        # Update the curve index
        indx += 1
    if self.cursor.display_mode == 'YYX':
      # Open the CSV file for writing the content
      with open(file=filename, mode='w') as csv_file:
        # Declare a writer object responsible for converting the user data into a string to write on a line
        writer = csv.writer(csv_file)
        # Write the header list on the first line
        writer.writerow(headers)

        # Get the X list common to all the curves
        x = curves[0].get_data()[0]

        # # Loop over all the X-values
        for i in range(0, len(x)):
          # Write the single line in the CSV file built as the i-th X value and the Y ones of all the curves
          writer.writerow([x[i]] + [xy.get_data()[1][i] for xy in curves_to_save.keys()])

    # Update the initial directory to the path of the saved file folder
    self.initial_dir = os.path.dirname(filename)

  def set_active_curves(self, active_curves: List[Line2D]) -> None:
    """
    Method that sets the instance attribute referring to the currently
    active curves, provided as a list of 'Line2D' objects.
    """
    self.active_curves = active_curves
    # Activate the 'SaveCSV' toolbar button as there are curves available
    self._buttons['savecsv'].configure(state='active')

  def set_axes(self, axes: Axes) -> None:
    """
    Method that sets the instance attribute referring to the current
    plot Axes object.
    """
    self.axes = axes
    # Activate the 'Legend' and 'Cursor' toolbar buttons as the Axes object has been defined
    self._buttons['legend'].configure(state='active')
    self._buttons['cursor'].configure(state='active')

  def _add_new_button(self, name: str, text: str, img_relpath: str,
                      toggle: bool, command: Callable, tooltip: str) -> None:
    """
    Method that allows to add a new button for the plot toolbar by providing its name, a descriptive
    text, the path to its image, relative to this module, if it has to be treated as an on/off button,
    the command to execute and a string providing the button tooltip.
    """
    # Add the button to the toolbar buttons dictionary
    self._buttons[name] = self._Button(
      text=text,
      image_file=os.path.join(os.path.abspath(os.path.dirname(__file__)), img_relpath),
      toggle=toggle,
      command=command)
    # Add the button to the toolbar
    self._buttons[name].pack(side=tk.LEFT)
    # Turn off the button if it is a Checkbutton
    if toggle:
      self._buttons[name].deselect()
    # Add a tooltip for the button
    _backend_tk.add_tooltip(self._buttons[name], tooltip)


class PlotCursor():
  """
  Class that provides the functionalities for showing a cursor on the plot curves. It is
  made by a vertical line, an annotation box and a marker for each of the active curves.
  The annotation box provides the active curves X-Y values corresponding to the cursor
  position; markers are also shown in the same position.
  The cursor can be dragged by the mouse and can assume positions given by the X-Y values
  of the active curves stored within the present instance.
  """
  def __init__(self, ax: Axes, x: List[ArrayLike], y: List[ArrayLike]) -> None:
    """
    Class constructor. It needs the plot Axes object, the X values and
    a list of Y-values for each curve.
    It initialize the instance attribute and couples mouse events to the
    execution of a different method.
    """
    # Do not instantiate certain attributes if the class is instantiated
    # without Axes object, i.e. when the plot figure is created, but no
    # curves are plotted yet.
    if ax != None:
      # Store the current plot Axes object
      self.ax: Axes = ax
      # Store the X-Y values into the corresponding instance variables by extracting
      # them from the corresponding curves.
      self.xs: List[ArrayLike] = x
      self.ys: List[ArrayLike] = y

      # Connect events on the plot area to the execution of the corresponding methods
      self._connect_events_to_methods()

    # Initialize a list holding the curves markers and labels
    self.marker: List[Line2D] = list()

    # Initialize flags for defining the cursor events
    self.moved: Union[bool, None] = None
    self.pressed: bool = False
    self.start: bool = False
    # Initialize to False the flag providing the cursor activation
    self.state: bool = False
    self.button_state: bool = False
    # Initialize a variable identifying the index for the curves X-Y lists
    self.indx: int = 0

  def activate_cursor(self) -> None:
    """
    Method that deals with the cursor activation. When called, it builds the cursor
    vertical line, the annotation box showing the curves Y-values at the cursor
    X-position, as well as the markers for each curve.
    In case the plotted curves have different values for the X-coordinates, the cursor
    X-position is calculated as the average among the values of the curves at the
    current common index of their lists.
    """
    # The cursor has to be activated, hence set its state to True
    self.state = True

    #################################################################################
    # Build and show the elements providing the cursor functionality, if the instance
    # attribute providing the plot Axes object has been set up.
    #################################################################################
    if not hasattr(self, 'ax'): return
    if len(self.xs) == 0: return
    print("ACTIVATING CURSOR...")
    # Initialize the marker list
    self.marker = list()

    # ----------------------------------------
    # Handle the cursor vertical line building
    # ----------------------------------------
    # Evaluate the X-coordinate of the cursor vertical line as the average of the
    # X-positions for the plotted curves, given by the stored index
    x_line_pos = sum(x[self.indx] for x in self.xs) / len(self.xs)
    # Build the cursor vertical line at the calculated X-position
    self.line_cursor = self.ax.axvline(x_line_pos, color='k', alpha=0.8)

    # -------------------------------------------------------------------
    # Handle the building of the annotation box showing the curves values
    # -------------------------------------------------------------------
    # Declare a list of empty strings with same dimension of the colors one
    texts = ['' for e in self.line_colors]
    # Declare a list of TextArea objects
    self.text_areas: List[TextArea] = list()
    # Loop over all the elements of both text and colors lists
    for t,c in zip(texts, self.line_colors):
      # Add a TextArea object, each with a different color (for Y-values)
      self.text_areas.append(TextArea(t, textprops=dict(color=c)))
    # Add another line, in case of the 'YYX' display mode
    if self.display_mode == 'YYX':
      # Append a last element with black color (for X-value)
      self.text_areas.append(TextArea('', textprops=dict(color='black')))

    # Instantiate a VPacker object that packs its children vertically, automatically
    # adjusting their relative positions at draw time
    self.values_box = VPacker(children=self.text_areas, pad=0, sep=0)

    # Transform in Axes coordinates the X-Y values of the point the annotation box refers to; given the
    # index providing the X-value closest to the current cursor position, the first curve is considered.
    xy = self.ax.transLimits.transform((self.xs[0][self.indx], self.ys[0][self.indx]))

    # Define the style of the annotation box showing the curves values
    box_style = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # Instantiate an AnnotationBbox object displaying the curves values at the cursor position.
    # Both the point to annotate and the box position are given in Axes coordinates.
    self.ann = AnnotationBbox(self.values_box,
                              xy=(xy[0], xy[1]),
                              xycoords=self.ax.transAxes,
                              box_alignment=(1.0, 1.1),
                              bboxprops=box_style)
    # Add the annotation box to the list of elements belonging to the Axes object
    self.ax.add_artist(self.ann)
    # Update the annotation box position so that it moves together with the line cursor
    self._update_box_coordinates()

    # Increase the upper limit of the Y-axis by the heigth of the annotation box
    # whose coordinates are converted in data coordinates.
    box_data_coords = self.ax.transData.inverted().transform(self.ann.get_window_extent())
    # Calculate the height of the box
    delta_y = box_data_coords[1][1] - box_data_coords[0][1]
    # Set the Y-axis upper limit increased by the annotation box height
    self.ax.set_ylim((self.ax.get_ylim()[0], self.ax.get_ylim()[1] + delta_y))

    ##########################################################################
    # Derive the X-Y values to show in the annotation as soon as it is enabled
    ##########################################################################
    # Declare a list holding the X-Y values to show
    values_text = list()
    # Handle the two different annotation display modes, i.e. curves with different
    # X-values ('X-Y') or curves with same X-values ('YYX')
    if self.display_mode == 'X-Y':
      # Loop over all the curves X-Y values lists
      for i, j in zip(self.xs, self.ys):
        # Get the X-Y value of the curve at the current index value
        x = i[self.indx]
        y = j[self.indx]
        # Add the current curve Y-value to the list that builds the text to show;
        # each value is provided with a 5 digits precision. If the value is smaller
        # than 1e-4, a scientific notation is used.
        if abs(x) > 1e-4:
          text = '• ' + '%1.5f, ' % (x)
        else:
          text = '• ' + '%1.5e, ' % (x)
        if abs(y) > 1e-4:
          text += '%1.5f' % (y)
        else:
          text += '%1.5e' % (y)
        # Add the built text to the list
        values_text.append(text)

        # Build a cursor marker for each curve at the current X-Y position
        m, = self.ax.plot(x, y, marker="o", color="crimson", zorder=3)
        # Append the marker object to its corresponding list
        self.marker.append(m)
    else:
      # Loop over all the curves Y-values lists
      for j in self.ys:
        # Get the Y-value of the curve at the current index value
        y = j[self.indx]

        # Add the current curve Y-value to the list that builds the text to show;
        # each value is provided with a 5 digits precision. If the value is smaller,
        # than 1e-4, a scientific notation is used.
        if abs(y) > 1e-4:
          values_text.append('• ' + '%1.5f' % (y))
        else:
          values_text.append('• ' + '%1.5e' % (y))

        # Build a cursor marker for each curve at the current X-Y position
        m, = self.ax.plot(self.xs[0][self.indx], y, marker="o", color="crimson", zorder=3)
        # Append the marker object to its corresponding list
        self.marker.append(m)

      # Append the X-value of the current position for the cursor, using a 5 digits precision and
      # a floating or scientific notation.
      if abs(self.xs[0][self.indx]) > 1e-4:
        values_text.append('x=%1.5f' % (self.xs[0][self.indx]))
      else:
        values_text.append('x=%1.5e' % (self.xs[0][self.indx]))

    # Update each TextArea object contained in the annotation box with the X-Y values of the curves
    for t, i in zip(self.text_areas, range(len(self.text_areas))):
      t.set_text(values_text[i])

    # Re-draw the figure
    self.figcanvas.draw_idle()

  def deactivate_cursor(self) -> None:
    """
    Method that deals with the cursor deactivation. When called, it removes the
    cursor vertical line, deleting the corresponding instance attribute, the
    annotation box showing the curves Y-values at the cursor X-position, as well
    as the markers for each curve.
    """
    # As the cursor has been deactivated, set its state to false
    self.state = False
    print("@Cursor state is off...")
    if not hasattr(self, 'line_cursor'): return
    print("DEACTIVATING CURSOR...")

    # Remove the cursor vertical line
    self.line_cursor.remove()
    self.__delattr__('line_cursor')

    # Remove the marker for each curve
    for m in self.marker:
      m.remove()

    # Remove the annotation box displaying the curves values at cursor position
    self.ann.remove()
    # Reset the Y-axis limits as no upper space for the annotation box is needed anymore
    self.ax.set_ylim(self.y_axis_lim)
    # Re-draw the figure
    self.figcanvas.draw_idle()

  def set_attributes(self, ax: Axes, lines: List[Line2D]) -> None:
    """
    Method for setting the Axes object of the plot, the X-Y values lists, and the list
    of colors used by each plot.
    It also registers mouse and changes in axes limits events to specific method calls.
    """
    # Check if no Axes object or if an empty list have been passed
    if not ax or not lines:
      # Raise an exception
      raise Exception("ERROR: method called without passing a valid Axes or 'lines' list object.")

    # Store the current plot Axes object
    self.ax = ax
    # Store the X-Y values into the corresponding instance variables by extracting
    # them from the corresponding curves.
    self.xs = [line.get_data()[0] for line in lines]
    self.ys = [line.get_data()[1] for line in lines]
    # Store the original Y-axis limits, used for reset purposes when the cursor is
    # switched off.
    self.y_axis_lim = self.ax.get_ylim()
    # Store the colors of each plotted line
    self.line_colors = [line.get_color() for line in lines]
    # Evaluate the cursor display mode according to the X-coordinates of the input curves
    self.display_mode: Literal['X-Y', 'YYX'] = self._evaluate_display_mode()
    print('Display mode is', self.display_mode)

    # Get the index from the X-values list that is closest to the current X-axis left limit.
    self.indx = min(np.searchsorted(self.xs[0], [self.ax.get_xlim()[0]])[0], len(self.xs[0]) - 1)

    # Store the FigureCanvasBase object corresponding to the current plot
    self.figcanvas = self.ax.figure.canvas
    # Connect events on the plot area to the execution of the corresponding methods
    self._connect_events_to_methods()

  def _evaluate_display_mode(self) -> str:
    """
    Method that evaluates the cursor display mode according to the X-coordinates of the
    input curves: if they all have the same X-values, the cursor shows an annotation box
    built with the curves Y-values each on one line, followed by the X-value. If the
    curves show different X-coordinates, the cursor shows an annotation box where each
    line provides the X-Y values of the displayed curves.
    The choice for the display mode is made by comparing the curves X-values in terms of
    both the length of the corresponding lists and the values at same indices.
    """
    # Loop over all the curves X-lists
    for i in range(1, len(self.xs)):
      # Compare the size of the current line X-list with the one of the first line
      if len(self.xs[0]) != len(self.xs[i]):
        print(f"WARNING: the first and the {i}-th curves have different sizes. \
              There might be problems with cursor showing curves values.")
        # Set the display mode and exit
        return 'X-Y'
      # Compare the X-values at corresponding indices
      for j in range(0, len(self.xs[i])):
        if self.xs[0][j] != self.xs[i][j]:
          # Set the display mode and exit
          return 'X-Y'
    # If here, return the 'YYX' mode (same X-values for all curves)
    return 'YYX'

  def set_button_state(self, button_state: bool) -> None:
    """
    Method that allows to set the instance variable storing the corresponding
    button state in the plot toolbar.
    """
    self.button_state = button_state

  def show_activeonly_curves_info(self, active_curves: List[Line2D]) -> None:
    """
    Method that, given a list of Line2D objects, set the instance attribute
    storing the currently active curves, i.e. those shown in the plot and
    not deselected from the legend.
    In addition, if all the curves are deselected, it handles the cursor
    deactivation.
    """
    print(f"A total of '{len(active_curves)}' active curves are currently shown...")
    # If the list of curves is empty, clear all the stored X-Y data and deactivate the cursor
    if not active_curves:
      # Clear the lists for the X and Y-s values
      self.xs = list()
      self.ys = list()
      # Deactivate the cursor
      self.deactivate_cursor()
      # Return as no curve is active
      return

    # Store the X-Y values into the corresponding instance variables by extracting
    # them from the corresponding curves.
    self.xs = [line.get_data()[0] for line in active_curves]
    self.ys = [line.get_data()[1] for line in active_curves]
    # Store the colors of each plotted line
    self.line_colors = [line.get_color() for line in active_curves]

    # Return immediately if the corresponding cursor button in the toolbar is not active
    if not self.button_state: return

    # Delete any previously stored object for markers and annotation box
    self.deactivate_cursor()
    # The cursor button in the toolbar is active, hence recall the method for re-drawing
    # the cursor given the new X-Y values.
    self.activate_cursor()

  def _connect_events_to_methods(self) -> None:
    """
    Method that handles the binding of the instance methods ot specific events happening
    within the plot area. In particular, we have:
    . the 'button_press_event' event: related to a mouse button press;
    . the 'button_release_event' event: related to the release of a mouse button;
    . the 'motion_notify_event' event: related to the movement of the mouse arrow;
    . the 'resize_event' event: related to a change in the size of the figure;
    . the 'axes_leave_event' event: related to the mouse arrow exiting the figure area;
    . the 'xlim_changed' and 'ylim_changed' events: related to a change in the plot X-Y limits.
    """
    # Connect the mouse button press event to the execution of the corresponding method
    self.figcanvas.mpl_connect('button_press_event', self._handle_mouse_press)
    # Connect the mouse button release event to the execution of the corresponding method
    self.figcanvas.mpl_connect('button_release_event', self._handle_mouse_release)
    # Connect the drag mouse event to the execution of the corresponding method
    self.figcanvas.mpl_connect('motion_notify_event', self._handle_mouse_move)
    # Connect the figure resize event to the execution of the corresponding method
    self.figcanvas.mpl_connect('resize_event', self._handle_resize)
    # Connect the leave axes area event for the mouse to the execution of same method for
    # the mouse button release event
    self.figcanvas.mpl_connect('axes_leave_event', self._handle_mouse_release)
    # Connect the X-Y axes limits change events to the corresponding methods calls
    self.ax.callbacks.connect('xlim_changed', self._handle_xylims_change)
    self.ax.callbacks.connect('ylim_changed', self._handle_xylims_change)

  def _handle_mouse_move(self, event: tk.Event) -> None:
    """
    Method that is called whenever the mouse move event happens. It allows to move the
    cursor, the annotation box showing the X-Y values, and the corresponding markers
    for each curve following the mouse drag action.
    During the movement, the markers follows the paths of the plotted curves, while
    the annotation box shows the X-Y data values the cursor current position corresponds
    to.
    """
    # Return immediately if the cursor is off
    if not self.state: return
    # Return immediately if any of the toolbar navigation buttons is already pressed
    if self.ax.get_navigate_mode() != None: return
    # Return immediately if the event is not in the plot axes
    if not event.inaxes: return
    # Return immediately if the mouse has not been pressed before the move event
    if not self.pressed: return
    # Set the flag stating that a movement action has started to True
    self.start = True

    # Given the X-coordinate of the event, get the index from the curves X-values list that
    # is closest to the current event
    self.indx = min(np.searchsorted(self.xs[0], [event.xdata])[0], len(self.xs[0]) - 1)

    # Evaluate the X-coordinate of the cursor vertical line as the average of the
    # X-positions for the plotted curves, given by the index closest to the event
    x_line_pos = sum(x[self.indx] for x in self.xs) / len(self.xs)
    # Set the X-coordinate of the cursor vertical line to the X-position closest
    # to the one of the event
    self.line_cursor.set_xdata([x_line_pos])

    # Update the markers position and the text in the annotation box given the curves
    # X-values at the current index
    self._update_curves_info([i[self.indx] for i in self.xs])
    # Update the annotation box position so that it moves together with the line cursor
    self._update_box_coordinates()

    # Re-draw the figure
    self.ax.figure.canvas.draw_idle()

  def _handle_mouse_press(self, event: tk.Event) -> None:
    """
    Method that is called whenever the mouse button press event
    happens to set the point corresponding to the X-coordinate of
    the event.
    """
    # Return immediately if the cursor is off
    if not self.state: return
    # Return immediately if any of the toolbar navigation buttons is already pressed
    if self.ax.get_navigate_mode() != None: return
    # Return immediately if the event is not in the plot axes
    if not event.inaxes: return
    if event.inaxes != self.ax: return
    if self.start: return
    # Having pressed the mouse button, set the corresponding flag to True
    self.pressed = True

  def _handle_mouse_release(self, event: tk.Event) -> None:
    """
    Method that is called whenever the mouse button release event
    happens to set the instance flags.
    """
    # Return immediately if the cursor is off
    if not self.state: return
    if self.ax.get_navigate_mode() != None: return
    # Return immediately if the event is not in the plot axes
    if not event.inaxes: return
    if event.inaxes != self.ax: return
    # In case the mouse button has been pressed, re-set the instance flags
    if self.pressed:
      self.pressed = False
      self.start = False
      self.obj = self.moved

  def _handle_resize(self, event: tk.Event) -> None:
    """
    Method that is called whenever an event related to a resize of the plot
    figure happens. Given the new figure size, it calls the method for
    updating the annotation box position, if any is active.
    """
    # Update the annotation box coordinates, if present
    if hasattr(self, 'ann'):
      self._update_box_coordinates()

  def _handle_xylims_change(self, event_ax: Axes) -> None:
    """
    Method that is called whenever an event related to a change in the X-axis
    range happens. Given the new limits, it calls the method for updating the
    annotation box position, if any is active, otherwise it updates the index
    value that corresponds to a value closest to the current X-axis left limit.
    """
    print("Updated xlims: ", event_ax.get_xlim())
    print("Updated ylims: ", event_ax.get_ylim())

    # Update the annotation box coordinates, if present
    if hasattr(self, 'ann'):
      self._update_box_coordinates()
    else:
      # Get the index of the X-values list that corresponds to a value closest to the current
      # X-axis left limit.
      self.indx = min(np.searchsorted(self.xs, [self.ax.get_xlim()[0]])[0], len(self.xs) - 1)
      # Increase the index by 1 in case the corresponding X-value is lesser than the current X-axis left limit
      if self.xs[self.indx] < self.ax.get_xlim()[0]:
        self.indx += 1

  def _update_box_coordinates(self) -> None:
    """
    Method that updates the position of the annotation box showing the X-Y values of the curves
    at the cursor position, if any has been defined.
    It also hides the annotation box if its position exits the plot area, identified by the
    current limits of the axes.
    """
    # Return immediately if no cursor has been declared
    if not hasattr(self, 'line_cursor'): return

    # Get the the width and height of the annotation box in display coordinates and convert
    # them in Axes coordinates
    box_data_coords = self.ax.transData.inverted().transform(self.ann.get_window_extent())
    # Calculate the width of the box
    delta_x = box_data_coords[1][0] - box_data_coords[0][0]
    # Set the annotation box coordinates with the X-one increased by the width of the box, so that, when
    # the box is shown, it always appears on the right of the cursor line.
    box_coords = self.ax.transLimits.transform(
        (self.line_cursor.get_xdata()[0] + delta_x, self.ax.get_ylim()[1])
      )
    # Update the box X-Y coordinates
    self.ann.xybox = (box_coords[0], box_coords[1])

    # Get the X-Y coordinates of the axes left limit
    axes_xy_left_lim = self.ax.transLimits.transform((self.ax.get_xlim()[0], self.ax.get_ylim()[0]))
    # Get the X-Y coordinates of the axes right limit
    axes_xy_right_lim = self.ax.transLimits.transform((self.ax.get_xlim()[1], self.ax.get_ylim()[1]))

    # Check if the annotation box position is within the limits imposed by the axes; if not, hide it
    # TODO capire come nascondere box
    if self.ann.xybox[0] < axes_xy_left_lim[0] or self.ann.xybox[0] > axes_xy_right_lim[0] + box_coords[0]:
      self.ann.set(visible=False)
    elif self.ann.xybox[1] < axes_xy_left_lim[1] or self.ann.xybox[1] > axes_xy_right_lim[1]:
      self.ann.set(visible=False)
    else:
      self.ann.set(visible = True)

  def _update_curves_info(self, x: List[ArrayLike]) -> None:
    """
    Method that updates the text shown by the annotation box. Given the current X-position
    of the cursor, provided as argument, it extract the Y-values for the plotted curves and
    build the text to show.
    It also updates the markers position of each curve on the basis of the current X-position
    of the cursor.
    """
    # Declare a list of strings providing the curves Y-value at the current cursor position
    values_text = list()

    if self.display_mode == 'X-Y':
      # Loop over all the curves
      for j in range(0, len(self.ys)):
        # Get the Y value for the current curve
        y = self.ys[j][self.indx]
        # Set the X-Y coordinates of the curve marker to the ones corresponding to the
        # given X-position of the cursor.
        self.marker[j].set_data([x[j]],[y])

        # Add the current curve Y-value to the list that builds the text to show;
        # each value is provided with a 5 digits precision. If the value is smaller,
        # than 1e-4, a scientific notation is used.
        if abs(x[j]) > 1e-4:
          text = '• ' + '%1.5f, ' % (x[j])
        else:
          text = '• ' + '%1.5e, ' % (x[j])
        if abs(y) > 1e-4:
          text += '%1.5f' % (y)
        else:
          text += '%1.5e' % (y)
        # Add the built text to the list
        values_text.append(text)
    else:
      # Loop over all the curves
      for j in range(0, len(self.ys)):
        # Get the Y value for the current curve
        y = self.ys[j][self.indx]
        # Set the X-Y coordinates of the curve marker to the ones corresponding to the
        # given X-position of the cursor.
        self.marker[j].set_data([x[j]],[y])

        # Add the current curve Y-value to the list that builds the text to show;
        # each value is provided with a 5 digits precision. If the value is smaller,
        # than 1e-4, a scientific notation is used.
        if abs(y) > 1e-4:
          values_text.append('• ' + '%1.5f' % (y))
        else:
          values_text.append('• ' + '%1.5e' % (y))

      # Append the X-value of the current position for the cursor, using a 5 digits precision and
      # a floating or scientific notation.
      if abs(self.xs[0][self.indx]) > 1e-4:
        values_text.append('x=%1.5f' % (self.xs[0][self.indx]))
      else:
        values_text.append('x=%1.5e' % (self.xs[0][self.indx]))

    # Update each TextArea object contained in the annotation box with the X-Y values of the curves
    for t, i in zip(self.text_areas, range(len(self.text_areas))):
      t.set_text(values_text[i])


class PlotManager():
  """
  Class that handles the plot creation by extracting the data provided by the output files
  produced by the TuPlot and TuStat executables.
  """
  def __init__(self, dat_file: str, plt_file: str, out_file: str="") -> None:
    # Set the instance attributes
    self.dat_file: str = dat_file
    self.plt_file: str = plt_file
    if out_file != "":
      self.out_file: str = out_file

    # Extract the plot information from the .plt file
    self._read_plt_file()
    # Extract the plot X-Y data from the .dat file
    self._read_dat_file()
    # Extract the content of the .out report file, if any has been provided
    if hasattr(self, 'out_file'):
      self._read_out_file()

  def plot(self, plotFigure: PlotFigure, plot_index: int = 111) -> None:
    """
    Method that, given the input PlotFigure object, configures the plots and shows
    the curves. The plot legend is configured so that each curve visibility can be
    toggled on/off.
    """
    # Get the Figure from PlotFigure instance
    fig = plotFigure.fig
    # Store a reference to the toolbar for the given PlotFigure object
    self.toolbar: CustomToolbar = plotFigure.toolbar
    # Reset the cursor state of the toolbar
    self.toolbar.cursor.deactivate_cursor()

    # ----------------------
    # Set-up the plot figure
    # ----------------------
    # Clear any previously drawn curve
    fig.clear()
    # Add a subplot at the given index
    axes = fig.add_subplot(plot_index)
    # Set the plot title
    axes.title.set_text(self.diagram_name)
    # Set the plot X-Y labels
    axes.set_xlabel(self.x_axis_name)
    axes.set_ylabel(self.y_axis_name)

    # Declare an array holding the X-Y data for each curve to plot
    lines: List[Line2D] = list()

    # Loop over all the curves stored in the dictionary extracted by reading the .dat file
    # and plot each of them
    for key, value in self.curves2plot.items():
      # Extract 2 lists, one for the X- and one for the Y-values of the current curve in the loop
      vals_x = np.array(value).T.tolist()[0]
      vals_y = np.array(value).T.tolist()[1]

      # print(key, vals_x, vals_y)

      # Plot the current curve with its label
      (line, ) = axes.plot(vals_x, vals_y, label = key)
      # Add the Line2D object to the curves list
      lines.append(line)

    # Configure the plot cursor by passing the axes and the Line2D objects containing the X-Y data
    # information (e.g. the curves color)
    self.toolbar.cursor.set_attributes(axes, lines)
    # Set the toolbar instance attribute corresponding to the plot Axes object
    self.toolbar.set_axes(axes)
    # Set the toolbar instance attribute corresponding to the plot Line2D objects representing the
    # currently active curves.
    self.toolbar.set_active_curves(lines)

    # Show the plot grid
    axes.grid()
    # Show the plot legend
    legend = axes.legend(fancybox=True, shadow=True)
    # Set the legend to be draggable
    legend.set_draggable(True)

    # Declare a map with keys being the curves Legend objects and values the corresponding Line2D object
    map_legend_to_ax = {}
    # Declare how close (in points) the click needs to be to trigger the plot legend pick event
    pickradius = 5
    # Join the legend Lined2D object with the corresponding Lined2D object of the curve and
    # loop over each tuple
    for legend_line, ax_line in zip(legend.get_lines(), lines):
      # Configure the pick event based on the selected radius
      legend_line.set_picker(pickradius)
      # Add the entry to the map
      map_legend_to_ax[legend_line] = ax_line

    # Connect the pick event to a function that manages the toggle on/off the visibility of the picked curve
    fig.canvas.mpl_connect('pick_event', func=lambda event: self._handle_legend_pick(event, fig, map_legend_to_ax))
    # Update the figure
    fig.canvas.draw()

    # Show the curves in the plot
    plt.show()

    # Show the plot report, if any is present
    if hasattr(self, 'out_file'):
      # Set the text area as editable
      plotFigure.text_widget.configure(state=tk.NORMAL)
      # Clear any previous content
      plotFigure.text_widget.delete(1.0, tk.END)
      # Insert all the content of the .out file into the report text area
      plotFigure.text_widget.insert(tk.END, self.report)
      # Disable the editability of the report text area
      plotFigure.text_widget.configure(state=tk.DISABLED)

  def _handle_legend_pick(self, event: tk.Event, fig: Figure,
                          map_legend_to_ax: Dict[Axes.legend, Line2D]) -> None:
    """
    Method that, given the pick event, changes the visibility of the curve selected
    from the plot legend.
    """
    # If the legend for the plot axis (index 0) is not visible, return immediately,
    # thus disabling this functionality.
    if not fig.get_axes()[0].get_legend().get_visible(): return

    # On the pick event, find the original line corresponding to the legend
    # line, and toggle its visibility.
    legend_line = event.artist

    # Do nothing if the source of the event is not a legend line.
    if legend_line not in map_legend_to_ax: return

    # Get the curve
    ax_line = map_legend_to_ax[legend_line]
    # Declare the visibility of the curve as the opposite of its current one
    is_visible = not ax_line.get_visible()
    # Change the curve visibility
    ax_line.set_visible(is_visible)
    # Change the alpha on the line in the legend, so the toggled lines can still be seen
    legend_line.set_alpha(1.0 if is_visible else 0.2)
    # Update the plot figure
    fig.canvas.draw()

    # Get the list of active-only curves
    active_curves = [curve for curve in map_legend_to_ax.values() if curve.get_visible()]
    # Pass the active curves to the cursor object
    self.toolbar.cursor.show_activeonly_curves_info(active_curves)
    # Pass the active curves to the toolbar object
    self.toolbar.set_active_curves(active_curves)

  def _read_dat_file(self) -> None:
    """
    Method for extracting the X-Y data for the curves to be plotted. A different reading method
    is used that is given by the presence of the '/td' string at the beginning of the file. This
    identifies two types of .dat files, i.e. the ones:
    . for 'Radius' and 'Axial' groups where the X-Y data is provided separately for each curve; it
      is also used by .dat produced from a statistical simulation.
    . for 'Time' and 'Time Integral' groups where the Y-values of the curves are provided on the
      same line for each X-value.
    Based on the type, this method builds an instance attribute that is a dictionary with keys being
    the plot legend and values the corresponding list of X-Y values as tuples.
    """
    # Check if the given .dat file corresponds to the one indicated in the .plt file
    if hasattr(self, 'dat_filename'):
      # Raise an exception if there is no correspondence
      if self.dat_filename != os.path.basename(self.dat_file):
        raise Exception(f"Error: the loaded '{self.plt_file}' file refers to the '{self.dat_filename}' "
                        f"which is different from the loaded '{self.dat_file}' file.")

    # Open the file and read its content
    with open(self.dat_file) as file:
      # Variable stating if the end of a curve section has been reached
      curve_end = False
      # List containing the X-Y values for every curve
      curve = list()
      # Dictionary containing the curves values with key the legend and value a list of X-Y values
      self.curves2plot: Dict[Union[List[str], str], List[Tuple[float]]] = dict()

      # Handle the .dat content reading differently on the basis of the first line of the .dat file:
      # . if it starts with '/td', the curves X-Y data are provided separately as in the 'Radius'
      #   and 'Axial' types. In these cases, the file also contains info about the legend.
      #   The same start line is also used for statistical diagrams; in this case, no legend is provided.
      # . if the '/td' string is not present, the curves X-Y data are provided all on the same line
      #   (for a given X-value). No legend information is present, which is retrieved from the already
      #   read .plt file.

      # Read the first line
      line = file.readline()
      if line.startswith('/td'):
        ############################################################################################
        # The .dat file provides curves X-Y data separately. It also contains info about the legend
        # (excluded the TuStat case).
        ############################################################################################
        # Loop over all the .dat file lines
        for line in file:
          # Initialize a flag identifying if the curve section has ended
          curve_end = False
          # Get the line without '\n' and any leading spaces
          line = line.strip()

          # Interpret the line content
          if line.startswith('//nc'):
            # End of curve tag
            curve_end = True
          elif line.startswith('//lt'):
            # Check for any match in the line for extracting the legend
            lgnd = re.search("\"\s*(.*?)\s*\".*(?=;legend.*$)", line)
            # If a match has been found, store the legend
            if lgnd:
              self.legend = self._render_mathtext(lgnd.group(1))
            print("CURVE LEGEND: " + self.legend)
          elif line.startswith('/'):
            # Skip any other configuration line
            continue
          else:
            # Result line -> extract the X-Y values
            (val_x, val_y) = line.split()
            # Add the tuple to the list after converting X and Y to float and substituting the Fortran
            # exponential 'D' character with 'E'
            curve.append((float(val_x.replace('D', 'E')), float(val_y.replace('D', 'E'))))

          # If the curve section has ended (but not the file), store the legend-list of values entry
          # into a dictionary.
          if curve_end:
            # Handle the cases where no legend is provided either in the .plt or the .dat files
            if not self.legend:
              # Use the Y-axis name as legend
              self.legend = self.y_axis_name
            # Add a new entry by copying the current curve list
            self.curves2plot[self.legend] = curve.copy()
            # Clear the current curve list
            curve.clear()
            # Reset the boolean flag for identifying the end of the curve section
            curve_end = False
        # Handle the case of a TuStat curve: the .dat file does not have the '//nc' end tag. Hence,
        # the curve values and its legend, if provided by the .plt file, are added to the dictionary.
        # If no legend is given, the Y-axis name is used.
        if not self.legend:
          self.curves2plot[self.y_axis_name] = curve.copy()
      else:
        ##############################################################################################
        # The .dat file provides curves X-Y data all on the same line (for a given X-value). No legend
        # information is present, which has already been retrieved from the already read .plt file.
        ##############################################################################################
        # Declare a list holding the X-data
        x: List[str] = list()
        # Declare a list of lists holding the Y-data for each curve
        ys: List[List[str]] = list()

        print("CURVE LEGEND 2: ", self.legend)

        # Go back to the beginning of the file
        file.seek(0)
        # Loop over all the .dat file lines
        for line in file:
          # Get the line without '\n' and any leading spaces
          line = line.strip()
          # Skip the line if it starts with "/"
          if line.startswith('/'):
            continue

          # Split the line content into a list
          items = line.split()
          # Add the first element to the X-data list
          x.append(items[0])
          # Add all the other elements to the Y-data list of lists
          ys.append(items[1:])

        # ----------------------------------------------------------------------------
        # Build the dictionary with legend-list of values entries: in case no legends
        # are provided in the .plt file, the plot indices are used.
        # ----------------------------------------------------------------------------
        # If no legend is present in the .plt file, use the plot indices as a legend
        if not self.legend:
          self.legend = [index for index in range(0, len(ys[0]))]
        # Loop over all the legends and initialize the entry lists for the dictionary
        for l in self.legend:
          self.curves2plot[l] = list()

        # Loop over all the X-values
        for i in range(0, len(x)):
          j = 0
          # Loop over all the legends
          for l in self.legend:
            # Add the X-Y data for the current curve by replacing the the Fortran exponential 'D'
            # character with 'E'
            self.curves2plot[l].append((float(x[i].replace("D", "E")), float(ys[i][j].replace("D", "E"))))
            j += 1

  def _read_out_file(self) -> None:
    """
    Method for extracting the content of the report .out file and saving it
    into a string instance attribute.
    """
    # Open the .plt file to read info about the quantities being plotted
    with open(self.out_file) as file:
      # Save all the file content into a string
      self.report = file.read()

  def _read_plt_file(self) -> None:
    """
    Method for extracting the data for setting up the plot display information,
    i.e. the axes names, the plot title, the plot legend, if present.
    """
    # Open the .plt file to read info about the quantities being plotted
    with open(self.plt_file) as file:
      # Labels for X and Y axes
      self.x_axis_name = ""
      self.y_axis_name = ""
      self.diagram_name = ""
      self.legend = list()

      # Loop over all the .dat file lines
      for line in file:
        # Get the line without '\n'
        line = line.split('\n')[0]
        # Extract the generic axis name from the line
        axis_name = re.search("\"\s*(.*?)\s*\".*(?=axis-title.*$)", line)
        # Extract the title of the plot
        plot_name = re.search("\"\s*(.*?)\s*\".*(?=;graph title.*$)", line)
        # Extract the name of the corresponding .dat file
        dat_filename = re.search("\"\s*(.*?)\s*\".*(?=;data file.*$)", line)

        # Extract the legend, if present
        lgd = re.search("\"\s*(.*?)\s*\".*(?=;legend for.*$)", line)

        # Assign the axes and the plot names to the corresponding variable on the basis of the presence of a specific label
        if "x-axis-title" in line and axis_name:
          self.x_axis_name = self._render_mathtext(axis_name.group(1))
        elif "y-axis-title" in line and axis_name:
          self.y_axis_name = self._render_mathtext(axis_name.group(1))
        elif "graph title" in line and plot_name:
          if self.diagram_name == "":
            self.diagram_name = self._render_mathtext(plot_name.group(1))
          else:
            self.diagram_name = self.diagram_name + "\n" + self._render_mathtext(plot_name.group(1))
        elif "legend" in line and lgd:
          self.legend.append(self._render_mathtext(lgd.group(1)))
        elif dat_filename:
          self.dat_filename = dat_filename.group(1)

      # Perform a check on the extracted legends: if any value is an empty string, replace it with the
      # name of the Y-axis
      for i in range(len(self.legend)):
        if not self.legend[i]:
          self.legend[i] = self.y_axis_name

  def _render_mathtext(self, text: str) -> str:
    """
    Method that, given the input string, allows its rendering as a mathematical expression.
    The string can contain some special characters that need to be interpreted as a
    mathematical expression:
    . "^{'some text'}": indicates a superscript
    . "_{'some text'}": indicates a subscript
    . "\ + 'a single letter'": indicates a greek letter
    A proper substitution is provided by this method in order that matplotlib can interpret
    the string as a mathtext.
    """
    # ---------------------------
    # Handle the superscript case
    # ---------------------------
    text = self._search_and_replace(text, '^')
    # -------------------------
    # Handle the subscript case
    # -------------------------
    text = self._search_and_replace(text, '_')
    # -----------------------------
    # Handle the greek letter cases
    # -----------------------------
    # Find all the occurrences of the substring '\letter' that indicates the letter to be interpreted as a greek symbol
    found_str = re.findall('\\\\(\w)', text)
    if found_str:
      # Loop over all the found occurrences
      for val in found_str:
        # Interpret the letter and substitute it with the corresponding substring as it is required by matplotlib
        text = re.sub('(?<!\$)(\\\\' + val[0] + ')(?!=\$)', '$\\\\' + self._interpret_matplotlib_symbol(val[0]) + '$', text)

    # Return the string with any performed modification
    return text

  def _interpret_matplotlib_symbol(self, letter: str) -> str:
    """
    Method that, given the input letter, returns a new one that corresponds
    to how matplotlib interprets the corresponding symbol.
    """
    match letter:
      # Lower-case
      case 'a': return 'alpha'
      case 'b': return 'beta'
      case 'c': return 'chi'
      case 'd': return 'delta'
      case 'e': return 'epsilon'
      case 'f': return 'phi'
      case 'g': return 'gamma'
      case 'h': return 'eta'
      case 'i': return 'iota'
      case 'j': return 'varphi'
      case 'k': return 'kappa'
      case 'l': return 'lambda'
      case 'm': return 'mu'
      case 'n': return 'nu'
      case 'o': return 'o'
      case 'p': return 'pi'
      case 'q': return 'theta'
      case 'r': return 'rho'
      case 's': return 'sigma'
      case 't': return 'tau'
      case 'u': return 'upsilon'
      case 'v': return 'varpi'
      case 'w': return 'omega'
      case 'x': return 'xi'
      case 'y': return 'psi'
      case 'z': return 'zeta'
      # Upper-case
      case 'A': return 'AA'
      case 'D': return 'Delta'
      case 'F': return 'Phi'
      case 'G': return 'Gamma'
      case 'I': return 'int'
      case 'J': return 'vartheta'
      case 'L': return 'Lambda'
      case 'P': return 'PI'
      case 'Q': return 'Theta'
      case 'S': return 'Sigma'
      case 'T': return 'infty'
      case 'U': return 'Upsilon'
      case 'V': return 'varsigma'
      case 'W': return 'Omega'
      case 'X': return 'Xi'
      case 'Y': return 'Psi'
      # Default case
      case _: return letter

  def _search_and_replace(self, text: str, search_char: str) -> str:
    """
    Method that, given the input string 'text', searches for any match of substrings that start
    with the input character.
    For any match, the substring is substituted with another one enclosed by a '$' symbol.
    """
    # Find all the occurrences identified by the search character followed by exactly one or more
    # if enclosed by '{}'
    found_str = re.findall(f'\{search_char}(\w)|\{search_char}' + '({\w*})', text)
    if found_str:
      # Loop over all the found occurrences
      for val in found_str:
        # Handle the two capturing groups matches separately
        if val[0]:
          text = re.sub(f'(?<!\$)(\{search_char}' + val[0] + ')(?!=\$)', f'${search_char}' + val[0] + '$', text)
        elif val[1]:
          text = re.sub(f'(?<!\$)(\{search_char}\\' + val[1] + ')(?!=\$)', f'${search_char}' + val[1] + '$', text)
    # Return the modified string
    return text


"""
Testing the module functionalities.
"""
if __name__ == "__main__":
  # Instantiate the root window
  root: tk.Tk = tk.Tk()
  # Instantiate the PlotManager class
  plt_manager: PlotManager = PlotManager(dat_file="../Input/TuPlot01.dat",
                            plt_file="../Input/TuPlot01.plt")
  # Instantiate a PlotFigure object
  plt_figure: PlotFigure = PlotFigure(root)
  plt_figure.pack(fill='both', expand=True)
  # Remove the report area
  plt_figure.report_frame.destroy()

  # Plot the curves
  plt_manager.plot(plt_figure)

  # Start the loop event
  root.mainloop()

  # TODO check posizione cursore con plot y negativi