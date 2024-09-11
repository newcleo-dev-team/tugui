import os
import tkinter as tk
from tkinter import ttk
from sv_ttk import set_theme

from abc import ABC, abstractmethod
from typing import Callable, List, Union
from gui_configuration import GuiPlotFieldsConfigurator
from plot_settings import FieldType, GroupType, PlotSettingsConfigurator, LabelledCombobox
from plot_builder import PlotFigure
from gui_widgets import OnOffClickableLabel, WidgetTooltip, SquareButton, CustomNotebook
from support import IDGA, IANT

class TabContentBuilder(ttk.Frame, ABC):
  """
  Class that builds the content of a tab of the given notebook instance, in terms of
  its widgets. It inherits from a frame object and presents two areas:
  . quick-access buttons: on the left-most part of the tab area
  . main paned window: it contains the configuration area on the left, while the plot
    area on the right.
  The plot area is provided as a paned window as well, where the plot figure is on the
  left, while a text area on the right. The latter is where the report produced by the
  TU plot executables is shown.
  """
  def __init__(self, container: ttk.Notebook,
               guiConfig: GuiPlotFieldsConfigurator,
               tab_name: str, state: str) -> None:
    """
    Build an instance of the 'TabContentBuilder' class that provides the content of a
    notebook tab as a frame. It receives as parameters:
    . container: a notebook object to which this instance is added
    . guiConfig: a 'GuiPlotFieldsConfigurator' object providing the available plot
      settings to be displayed by this instance widgets
    . tab_name: a string specifying the name of the tab
    . state: a string describing the tab state
    """
    # Call the superclass constructor
    super().__init__(container)

    # Store the GUI configuration
    self.gui_config: GuiPlotFieldsConfigurator = guiConfig

    # Build the tab content
    self._build_tab_content(container, tab_name, state)

  def get_active_plotFigure(self) -> List[PlotFigure]:
    """
    Method that returns the 'PlotFigure' instance of the currently active tab of the
    notebook displaying the plots.
    """
    # Get the active plot tab index, if any tab is present
    active_tab_index = self.get_active_plot_tab_index()
    # Extract the list of 'PlotFigure' objects of the active tab
    plotFigures = [plotFig for plotFig in self.plotTabControl.winfo_children() if isinstance(plotFig, PlotFigure)]
    # Return the 'PlotFigure' object corresponding to the index of the currently active tab
    return plotFigures[active_tab_index]

  def get_active_plot_tab_index(self) -> int:
    """
    Method that returns the active tab index of the notebook used for displaying
    the plots. If there are no active tabs available because they are all closed,
    an exception is raised.
    """
    try:
      # Get the active plot tab index
      return self.plotTabControl.index('current')
    except Exception as e:
      self.run_button.configure(state=tk.DISABLED)
      raise Exception("No plot figures are currently present. Please, create a new one first.")

  def run_plot(self, func: Union[Callable, None] = None) -> None:
    """
    Method for storing the input function as an instance attribute, if any
    is provided.
    """
    # Store the function, if any is provided
    if func != None:
      self.run_func = func

  def set_slice_list(self, slices: List[str]) -> None:
    """
    Method for setting the list of strings used for populating the slice
    field in the plot configuration area.
    """
    self.slice_settings = slices

  @abstractmethod
  def set_times(self, **kwargs) -> None:
    """
    Abstract method that allows to set the instance attributes that corresponds
    to the simulation step times.
    This method, being an interface, will be overridden by subclasses providing
    their specific implementation.
    """

  def _add_new_plot_figure(self, plot_name: str) -> None:
    """
    Method that adds a new 'PlotFigure' object to this instance notebook.
    Given the prefix input string, this method assigns a name to the
    built tab by adding an integer, representing the plot index, to the
    provided string.
    A check on the already used names is performed so that no duplicate
    names (i.e. with same index) are present.
    """
    # Activate the show/hide report clickable label by generating the corresponding virtual event
    self.event_generate("<<ActivateReportButton>>")

    self.run_button.configure(state=tk.NORMAL)

    # Instantiate a new PlotFigure object and add it to the notebook grid
    new_plot = PlotFigure(self.plotTabControl)
    new_plot.grid(column=0, row=0)

    # Get the names of the available PlotFigure tabs
    list_of_tab_names = list()
    # Loop over all the available tab indexes
    for item in range(0, self.plotTabControl.index('end')):
      # Add the tab name to the list
      list_of_tab_names.append(self.plotTabControl.tab(item, 'text'))

    # Loop over all the available tab indexes
    for item in range(0, self.plotTabControl.index('end')):
      # If the tab name, given by the current index, is not in the list of
      # tab names, add the tab by passing the current tab name
      if not (plot_name + str(item+1)) in list_of_tab_names:
        self.plotTabControl.add(new_plot, text=plot_name + str(item + 1))
        # Change focus to the just created tab
        self.plotTabControl.select(self.plotTabControl.index('end')-1)
        # The tab has been added, hence return
        return

    # If here, add the tab with name given by the size of the available tabs + 1
    self.plotTabControl.add(new_plot, text=plot_name + str(self.plotTabControl.index('end') + 1))
    # Change focus to the just created tab
    self.plotTabControl.select(self.plotTabControl.index('end')-1)

  @abstractmethod
  def _build_configuration_fields(self, config_area: ttk.LabelFrame) -> None:
    """
    Abstract method for building the plot configuration fields area, provided as
    input. This method, being an interface, will be overridden by subclasses
    providing their specific implementation.
    """
    return

  def _build_plot_config_area(self, paned_window: ttk.PanedWindow) -> ttk.Frame:
    """
    Method for building the plot configuration area as a frame holding a 'LabelFrame'
    object within which the configuration fields and a button object for running the
    plot executables are provided.
    """
    # Instantiate a frame within the given paned window
    frame = ttk.Frame(paned_window)
    # Place the frame into the given paned window grid
    frame.grid(column=0, row=0, sticky='nsew')
    # Configure the frame in terms of its row and column
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # Instantiate a 'LabelFrame' where the plot configuration fields will be put
    config_area = ttk.LabelFrame(frame, text="Plot configuration")
    # Place the label frame into the main frame
    config_area.grid(column=0, row=0, sticky='nsew', padx=5, pady=5)
    # Configure the label frame in terms of its columns
    config_area.grid_columnconfigure(0, weight=0)
    config_area.grid_columnconfigure(1, weight=3)

    # Build the plot configuration fields (case-specific)
    self._build_configuration_fields(config_area)

    # Instantiate a button that calls an an external function
    self.run_button = ttk.Button(config_area, text="Run", state=tk.DISABLED, command=lambda: self.run_func())

    # Return the built frame
    return frame

  def _build_plot_figure(self, container: tk.Misc) -> ttk.Frame:
    """
    Method that builds the content of the area where the selected TU quantities are plotted.
    A Frame object, placed within the input container, holds the content of the plot area,
    within which there are:
    . 'CustomNotebook' instance: it provides a notebook whose tabs can be closed. A default
      tab is added, containing a 'PlotFigure' object providing the matplotlib figure and the
      corresponding toolbar.
    . 'AddNewPlotButton' instance: it provides a square size button for adding a new plot tab to the
      built notebook.
    Both elements are placed within the frame grid.
    """
    # Build a frame that holds the notebook whose tabs contain a 'PlotFigure' object
    frame = ttk.Frame(container)
    # Declare row/columns of the frame
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)
    frame.grid_rowconfigure(0, weight=1)

    # Declare a style fot the 'CustomNotebook' object so to add a bit of margin on the top
    s = ttk.Style()
    s.configure("CustomNotebook", tabmargins=[0, 5, 0, 0])
    # Instantiate the 'CustomNotebook' object and place it into the grid
    self.plotTabControl = CustomNotebook(frame, style='CustomNotebook')
    # The tab can span 2 columns so to overlap with the following button
    self.plotTabControl.grid(column=0, row=0, columnspan=2, sticky='nsew')

    # Declare a custom style to be assigned to the button
    s = ttk.Style()
    s.configure('add_button.TButton', font=('Helvetica', 10))
    # Instantiate the 'SquareButton' object for adding a new plot tab
    add_button = SquareButton(frame,
                              text="+",
                              size=30,
                              style='add_button.TButton',
                              command=lambda: self._add_new_plot_figure("Plot "))
    # Place the button in the frame grid (upper right corner)
    add_button.grid(column=1, row=0, sticky='ne')

    # Build the plot frame where the plots are shown
    plotFigure = PlotFigure(self.plotTabControl)
    # Place the plot frame within the tab grid
    plotFigure.grid(column=0, row=0)

    # Add the just built plot frame to the notebook
    self.plotTabControl.add(plotFigure, text="Plot 1")

    # Return the just built frame object
    return frame

  def _build_quick_access_buttons(self, panedwindow: ttk.PanedWindow) -> None:
    """
    Method that builds a quick-access area with utility buttons to collapse the lateral
    panes of the window.
    """
    # Build a frame into this class instance
    qab_area = ttk.Frame(self)
    # Place the frame into this class instance grid adding a vertical padding
    qab_area.grid(column=0, row=0, sticky='nsew', pady=5)
    # Configure this frame in terms of rows/columns
    qab_area.grid_columnconfigure(0, weight=1)
    qab_area.grid_rowconfigure((0, 1), weight=0)
    # qab_area.grid_anchor('s')

    # Add a button-like label for allowing users to show/hide the plot configuration area
    hide_show_config_button = OnOffClickableLabel(
      qab_area,
      size=24,
      image=[os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/showtab.png"),
             os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/hidetab.png")],
      command=lambda: self.expand_collapse_config_area(panedwindow))
    hide_show_config_button.grid(column=0, row=0, sticky='ew', padx=(2, 2), pady=(2, 2))
    # Add a tooltip for the button
    WidgetTooltip(hide_show_config_button, "Hide/Show the configuration area")

    # Add a button-like label for allowing users to show/hide the plot report area
    hide_show_report_button = OnOffClickableLabel(
      qab_area,
      size=24,
      rotation=180,
      image=[os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/showtab.png"),
             os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/hidetab.png")],
      command=self.expand_collapse_report_area)
    hide_show_report_button.grid(column=0, row=1, sticky='ew', padx=(2, 2), pady=(2, 2))
    # Add a tooltip for the button
    WidgetTooltip(hide_show_report_button, "Hide/Show the report area")

    # Bind the event of changing the tab to a method call that sets the report button state to one
    # corresponding to report area presence.
    self.plotTabControl.bind("<<NotebookTabChanged>>", lambda event: self.handle_tab_change(event, hide_show_report_button))
    # Bind the following virtual events to the execution of the corresponding method of the
    # 'OnOffClickableLabel' instance for de-/activating the label that shows/hides the
    # report area.
    self.bind("<<DeactivateReportButton>>", lambda event: hide_show_report_button.deactivate_label())
    self.bind("<<ActivateReportButton>>", lambda event: hide_show_report_button.activate_label())

  def _build_tab_content(self, container: ttk.Notebook, tab_name: str, state=tk.NORMAL) -> None:
    """
    Method that builds the content of a tab held by the input Notebook object. Its name and
    state (default value to NORMAL, meaning the tab is active) are provided as input as well.
    The content of the tab is given by:
    . quick-access buttons area: on the left-most part of the tab
    . main paned window: it contains the configuration area on the left, while the plot
      area on the right.
    The columns of the paned window are configured to have the plot area being able to resize
    3-times the settings area.
    """
    # Configure the tab frame in terms of rows and columns
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=0)
    self.grid_columnconfigure(1, weight=1)

    # Instantiate a PanedWindow object within the Frame with a column separator
    # that can slide horizontally
    paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
    # Place the paned window within the tab frame grid
    paned_window.grid(column=1, row=0, sticky='nsew')
    # Configure the paned window in terms of rows and columns: the right column can expand
    # 3-times the left one
    paned_window.rowconfigure(0, weight=1)
    paned_window.columnconfigure(0, weight=1)
    paned_window.columnconfigure(1, weight=3)

    # Build the plot configuration area and add it to the left side of the paned window
    paned_window.add(self._build_plot_config_area(paned_window))
    # Build the plot area and add it to the right side of the paned window
    paned_window.add(self._build_plot_figure(paned_window))

    # Add a new column to the left-most part of the tab for quick access buttons
    # (open/close config area and report one)
    self._build_quick_access_buttons(paned_window)

    # Add the just built frame to the notebook
    container.add(self, text=tab_name, state=state)

  def expand_collapse_config_area(self, panedwindow: ttk.PanedWindow) -> None:
    """
    Method that, given the input 'PanedWindow' object, collapses or expands the plot
    configuration section. This object is associated to an instance attribute that
    is saved when the area has to be collapsed, whereas the attribute is deleted
    when the area has to be expanded.
    The pane collapse result is provided by calling the 'remove()' method of the
    'PanedWindow' instance, which hides the pane.
    Since the pane is saved into an instance variable, it can be displayed again by
    calling the 'PanedWindow' 'insert()' method.
    """
    # Check if the instance attribute holding the pane object is present
    if hasattr(self, 'config_area'):
      # Add the pane object to the beginning of the PanedWindow
      panedwindow.insert(0, self.config_area)
      # Delete the instance attribute holding the pane object
      delattr(self, 'config_area')
    else:
      # Store the first pane object of the given PanedWindow
      self.config_area = panedwindow.panes()[0]
      # Hide the pane object from the given PanedWindow
      panedwindow.remove(self.config_area)

  def expand_collapse_report_area(self) -> None:
    """
    Method that, given the input 'PanedWindow' object, collapses or expands the plot
    report section. This object is associated to an instance attribute that is saved
    when the area has to be collapsed, whereas the attribute is deleted when the area
    has to be expanded.
    The pane collapse result is provided by calling the 'remove()' method of the
    'PanedWindow' instance, which hides the pane.
    Since the pane is saved into an instance variable, it can be displayed again by
    calling the 'PanedWindow' 'insert()' method.
    """
    # Get the 'PlotFigure' instance from the currently active tab of the plots notebook
    active_plotFigure = self.get_active_plotFigure()

    # Get the list of instances of the tk.PanedWindow class for the active plot figure and select the
    # first one, as only one is present
    active_pw = [i for i in active_plotFigure.winfo_children() if isinstance(i, ttk.PanedWindow)][0]

    # Check if the active PanedWindow has an attribute holding the pane object
    if hasattr(active_pw, 'report_area'):
      # Add the pane object to the end of the PanedWindow
      active_pw.insert('end', active_pw.report_area, weight=1)
      # Delete the active PanedWindow instance attribute holding the pane object
      delattr(active_pw, 'report_area')
    else:
      # Store the second pane object (only 2 are present) of the given PanedWindow
      active_pw.report_area = active_pw.panes()[1]
      # Hide the pane object from the given PanedWindow
      active_pw.remove(active_pw.report_area)

  def handle_tab_change(self, event: tk.Event,
                        hide_show_report_button: OnOffClickableLabel) -> None:
    """
    Method that is called whenever a plot tab is changed. It retrieves the 'PanedWindow' object
    of the 'PlotFigure' for the currently active tab.
    If no plot tabs are present, because they are all closed, the button for hiding/showing the
    report area is deactivated.
    If there are more than one active panes, but the corresponding button, that shows/hides the
    report area, is in 'Off' state, it is set to 'On', as it must be like that.
    If there is only one pane active (the plot one), but the report button state is 'On', it is
    set to 'Off', as it must be like that.
    """
    # Return immediately if no plot tabs are present
    if not self.plotTabControl.tabs():
      # Deactivate the button for hiding/showing the report area
      hide_show_report_button.deactivate_label()
      return

    # Get the 'PlotFigure' instance from the currently active tab of the plots notebook
    active_plotFigure = self.get_active_plotFigure()

    # Get the list of instances of the ttk.PanedWindow class for the active plot figure and select the
    # first one, as only one is present
    active_pw = [i for i in active_plotFigure.winfo_children() if isinstance(i, ttk.PanedWindow)][0]

    # Check the number of available panes in the PanedWindow: if more than one, the button state
    # should be on, while the contrary if only one pane is present. The button method for changing
    # its state (and image) is called without providing a function to run.
    if len(active_pw.panes()) > 1 and hide_show_report_button.on_state == False:
      hide_show_report_button.on_click()
    elif len(active_pw.panes()) == 1 and hide_show_report_button.on_state:
      hide_show_report_button.on_click()


class TuPlotTabContentBuilder(TabContentBuilder):
  """
  Class that builds the content, in term of its widgets, of the 'TuPlot' tab of the
  notebook instance contained in the GUI. It inherits from the 'TabContentBuilder'
  class, which provides the tab structure in terms of two areas:
  . quick-access buttons: on the left-most part of the tab area
  . main paned window: it contains the configuration area on the left, while the plot
    area on the right.
  While keeping the same structure, this class implements the widgets contained in
  the configuration area, as they are specific of the 'TuPlot' case.
  """
  iant_entry: LabelledCombobox = None
  additional_frame: ttk.Frame = None

  def __init__(self, container: ttk.Notebook,
               guiConfig: GuiPlotFieldsConfigurator,
               tab_name: str, state: str) -> None:
    """
    Build an instance of the 'TuPlotTabContentBuilder' class that provides the content of a
    notebook tab. It receives as parameters:
    . container: a notebook object to which this instance is added
    . guiConfig: a 'GuiPlotFieldsConfigurator' object providing the available plot settings
      to be displayed by this instance widgets
    . tab_name: a string specifying the name of the tab
    . state: a string describing the tab state
    The superclass constructor is called passing the needed parameters.
    """
    # Call the superclass constructor for building the tab content. The superclass methods are
    # here overridden by ones specific to the content to add.
    super().__init__(container, guiConfig, tab_name, state)
    # Specify the text of the button for running the plot executable
    self.run_button.configure(text='Run TuPlot')

  def set_times(self, **kwargs) -> None:
    """
    Method that allows to set the instance attributes for the simulation
    macro and micro step times.
    """
    # Check if the correct arguments have been passed to the method
    if not 'macro_time' in kwargs:
      raise Exception("Error in passing arguments to this function. The macro step times\
                      'macro_time' argument is missing.")
    if not 'micro_time' in kwargs:
      raise Exception("Error in passing arguments to this function. The micro step times\
                      'mairo_time' argument is missing.")
    # Store the times in the corresponding instance attributes
    self.macro_time = kwargs['macro_time']
    self.micro_time = kwargs['micro_time']

  def _activate_additional_settings(self, box_to_check: ttk.Combobox,
                                    container: ttk.Frame, row: int) -> None:
    """
    Method that is called whenever the "Number" or the "Type" combobox values are selected.
    It checks if the other combobox is selected and, if so, it activates the frame that
    holds the additional settings for configuring the plot to produce.
    """
    # Declare a row index for taking into account where to place the additional widgets
    row_index = 0

    # Check if the other combobox has been selected
    if box_to_check.get():
      # Different behaviour for plot numbers 102-108 and 113
      if any(str(num) in self.number_var.get() for num in self.gui_config.iant1[0]):
        # Plot number 113
        print(self.number_var.get())
        # Rebuild the frame for the additional configuration fields and add one for
        # allowing the setting of the temperature distribution choice
        row_index = self._build_iant_field(
          container, row, "Temp. distr.: ", self.gui_config.iant1[1], row_index, IANT.IANT_1.description)
      elif any(str(i) in self.number_var.get() for i in self.gui_config.iant2[0]):
        # Plot numbers 102-108
        print(self.number_var.get())
        # Rebuild the frame for the additional configuration fields and add one for
        # allowing the setting of the radiation stress choice
        row_index = self._build_iant_field(
          container, row, "Rad. Struct.: ", self.gui_config.iant2[1], row_index, IANT.IANT_2.description)
      else:
        # Destroy the additional fields
        print("DESTROY")

        # Clear out the stress or the temperature-related field, if present
        if self.iant_entry:
          self.iant_entry.destroy_fields()
          self.iant_entry = None
          delattr(self, 'iant')
        if self.additional_frame:
          self.additional_frame.destroy()
          self.additional_frame = None
        # Re-build the frame
        self.additional_frame = self._build_frame(container, row)
        # Disable the button for running the plot executable as the additional fields need to be set yet
        self.run_button.configure(state=tk.DISABLED)
        # Reset the row index
        row_index = 0

      # Build a dictionary between the "Group" field values and the GroupType enum values
      self.groupvalVSgrouptype = {list(self.gui_config.groupVSnumVsKn.keys())[0]: GroupType.group1,
                                  list(self.gui_config.groupVSnumVsKn.keys())[1]: GroupType.group2,
                                  list(self.gui_config.groupVSnumVsKn.keys())[2]: GroupType.group2A,
                                  list(self.gui_config.groupVSnumVsKn.keys())[3]: GroupType.group3}
      # Instantiate the class for the additional plot settings
      self.plt_sett_cfg = PlotSettingsConfigurator(self.additional_frame,
                                                   group=self.groupvalVSgrouptype[self.group.var.get()],
                                                   row_index=row_index)
      # Configure the fields
      self._configure_additional_fields(self.groupvalVSgrouptype[self.group.var.get()])

      # Change the run button state when elements are selected in every additional field
      self.additional_frame.bind('<<PlotSettingsSet>>', func=lambda event: self.run_button.configure(state=tk.ACTIVE))

  def _activate_fields(self, event: Union[tk.Event, None] = None,
                       number: Union[ttk.Combobox, None] = None,
                       type: Union[ttk.Combobox, None] = None) -> None:
    """
    Method that activates the "Number" and "Type" fields whenever the user chooses a value
    for the "Group" field in the plot settings area.
    These fields are first cleared out of any previous value and then populated accordingly
    with elements that correspond to the "Group" field choice. Users can only choose among
    the available values as the combobox fields are set as "read-only".
    """
    # Clear the previously set values
    number.set('')
    type.set('')

    # Set the "Number" field state as read-only
    number['state'] = "readonly"
    # Set the available values for the "Number" field, given the "Group" field choice
    number['values'] = tuple(self.gui_config.groupVSnumVsKn[self.group.var.get()].keys())
    # Set the "Type" field state as read-only
    type['state'] = "readonly"
    # Set the available values for the "Type" field, given the "Group" field choice
    type['values'] = tuple(self.gui_config.groupVStype[self.group.var.get()])

    # Destroy any additional field previously created by a different choice of the main fields
    if self.iant_entry:
      self.iant_entry.destroy_fields()
      self.iant_entry = None
      delattr(self, 'iant')
    if hasattr(self, 'plt_sett_cfg'):
      # Destroy the additional configuration fields
      self.plt_sett_cfg.destroy_fields()
      # Delete the corresponding attribute
      delattr(self, 'plt_sett_cfg')
    if self.additional_frame:
      self.additional_frame.destroy()
      self.additional_frame = None

    # Hide the button for running the plot executable
    self.run_button.grid_remove()

  def _build_iant_field(self, container: tk.Misc, row, label: str,
                        values: List[str], row_index: int, iant: IANT) -> int:
    """
    Method that builds a field for setting the IANT value in case the plot number is any
    in the range 102-108 (for radiation stress related cases) or the 113 one (for
    temperature distribution related case).
    This field is placed in the first row of a frame that holds the additional setup
    fields.
    """
    if self.iant_entry:
      self.iant_entry.destroy_fields()
      self.iant_entry = None
      delattr(self, 'iant')
    if self.additional_frame:
      self.additional_frame.destroy()
      self.additional_frame = None

    # Build the frame
    self.additional_frame = self._build_frame(container, row)
    # Add a field for allowing the setting of the IANT1/2 choice
    self.iant_entry = LabelledCombobox(self.additional_frame, 0, label, values)
    # Store the value of the IANT enumeration
    self.iant = iant
    # Update the row index
    return row_index + 1

  def _build_configuration_fields(self, config_area: ttk.LabelFrame) -> None:
    """
    Method that builds the fields, in terms of the widgets, enabling the user to
    configure the quantities to plot for a 'TuPlot' case. This method overrides
    the one already present in the 'TabContentBuilder' superclass, thus providing
    the specific implementation of the widgets for the frame provided as input.
    """
    # Build the "Group" setup made of a label and a combobox, disabled by default
    self.group = LabelledCombobox(config_area, 0, "Group: ", tuple(self.gui_config.groupVSnumVsKn.keys()), tk.DISABLED)
    # Increase the combobox width a little bit to better show items
    self.group.cbx.configure(width=25)

    # Build the "Number" setup made of a label and a combobox, disabled until the "Group" field is undefined
    number = LabelledCombobox(config_area, 1, "Number: ", list(), tk.DISABLED)
    # Declare a variable holding the "Number" field choosen value
    self.number_var = number.var

    # Build the "Type" setup made of a label and a combobox, disabled until the "Group" field is undefined
    type = LabelledCombobox(config_area, 2, "Type: ", list(), tk.DISABLED)
    # Declare a variable holding the "Type" field choosen value
    self.type_var = type.var

    # Bind the activation of the "Number" and "Type" fields to the "Group" field item selection
    self.group.cbx.bind('<<ComboboxSelected>>', func=lambda event: self._activate_fields(number=number.cbx, type=type.cbx))
    # Bind the activation of the additional settings fields to the selection of values for the "Group",
    # "Number" and "Type" fields
    number.cbx.bind('<<ComboboxSelected>>', func=lambda event: self._activate_additional_settings(type.cbx, config_area, 3))
    type.cbx.bind('<<ComboboxSelected>>', func=lambda event: self._activate_additional_settings(number.cbx, config_area, 3))

  def _build_frame(self, container: tk.Misc, row: int) -> ttk.Frame:
    """
    Method that builds and returns a frame within the given container object.
    It also places the frame within the container at the specified row index
    provided as input.
    """
    # Instantiate the frame
    frame = ttk.Frame(container)
    # Place the frame within the container grid at the specified row index
    frame.grid(column=0, row=row, columnspan=3, sticky='news')
    # Configure the frame in terms of its columns and of how much space each
    # one should take when resing the window
    frame.grid_columnconfigure(0, weight=0)
    frame.grid_columnconfigure(1, weight=3)
    # Return the just built frame
    return frame

  def _configure_additional_fields(self, group: GroupType) -> None:
    """
    Method for configuring the values of the additional plot settings fields, provided by the
    'PlotSettingsConfigurator' instance, according to the choices made for the "Type" field.
    In particular, if the type is:
    . IDGA 1 (i.e. curves for different Kn): comboboxes allow to set the plot slice number
      and the reference time, while the listbox the curves Kn-s
    . IDGA 2 (i.e. curves for different times): comboboxes allow to set the plot slice number
      and the curve Kn, while the listbox the different times
    . IDGA 3 (i.e. curves for different slices): comboboxes allow to set the curve Kn and the
      reference time, while the listbox the different slices numbers
    """
    # Select either the macro o the micro time instant to display
    if (group == GroupType.group1):
      time_to_show = self.macro_time
    else:
      time_to_show = self.micro_time

    # Handle the different curve types (IDGA value)
    if (self.type_var.get() == IDGA.IDGA_1.description):
      # Case of curves for different Kn-s --> IDGA 1
      print("IDGA is: " + IDGA.IDGA_1.description)
      # Configure the fields
      self.plt_sett_cfg.configure_fields(
          "Slice: ", self.slice_settings,
          "Time (h s ms): ", time_to_show,
          "Select Curve(s)", self.gui_config.groupVSnumVsKn[self.group.var.get()][self.number_var.get()])
      # Set the fields type (1. Slice, 2. Time, 3. Kn)
      self.plt_sett_cfg.set_fields_type(FieldType['type3'], FieldType['type2'], FieldType['type1'])

    elif (self.type_var.get() == IDGA.IDGA_2.description):
        # Case of curves for different times --> IDGA 2
        print("IDGA is: " + IDGA.IDGA_2.description)

        # Configure the fields
        self.plt_sett_cfg.configure_fields(
            "Slice: ", self.slice_settings,
            "Curve: ", self.gui_config.groupVSnumVsKn[self.group.var.get()][self.number_var.get()],
            "Select Time(s)", time_to_show)
        # Set the fields type (1. Slice, 2. Kn, 3. Time)
        self.plt_sett_cfg.set_fields_type(FieldType['type3'], FieldType['type1'], FieldType['type2'])

    elif (self.type_var.get() == IDGA.IDGA_3.description):
        # Case of curves for different slices --> IDGA 3
        print("IDGA is: " + IDGA.IDGA_3.description)

        # Configure the fields
        self.plt_sett_cfg.configure_fields(
            "Curve: ", self.gui_config.groupVSnumVsKn[self.group.var.get()][self.number_var.get()],
            "Time (h s ms): ", time_to_show,
            "Select Slice(s)", self.slice_settings)
        # Set the fields type (1. Kn, 2. Time, 3. Slice)
        self.plt_sett_cfg.set_fields_type(FieldType['type1'], FieldType['type2'], FieldType['type3'])

    # Show the run button by adding it to the configuration area frame just below the frame holding
    # the additional configuration fields
    self.run_button.grid(column=1, row=self.additional_frame.grid_info()['row'] + 1, sticky='e')


class TuStatTabContentBuilder(TabContentBuilder):
  """
  Class that builds the content, in term of its widgets, of the 'TuStat' tab of the
  notebook instance contained in the GUI. It inherits from the 'TabContentBuilder'
  class, which provides the tab structure in terms of two areas:
  . quick-access buttons: on the left-most part of the tab area
  . main paned window: it contains the configuration area on the left, while the plot
    area on the right.
  While keeping the same structure, this class implements the widgets contained in
  the configuration area, as they are specific of the 'TuStat' case.
  """
  def __init__(self, container: ttk.Notebook,
               guiConfig: GuiPlotFieldsConfigurator,
               tab_name: str, state: str) -> None:
    """
    Build an instance of the 'TuStatTabContentBuilder' class that provides the content of a
    notebook tab. It receives as parameters:
    . container: a notebook object to which this instance is added
    . guiConfig: a 'GuiPlotFieldsConfigurator' object providing the available plot settings
      to be displayed by this instance widgets
    . tab_name: a string specifying the name of the tab
    . state: a string describing the tab state
    The superclass constructor is called passing the needed parameters.
    """
    # Call the superclass constructor for building the tab content. The superclass methods are
    # here overridden by ones specific to the content to add.
    super().__init__(container, guiConfig, tab_name, state)
    # Specify the text of the button for running the plot executable
    self.run_button.configure(text='Run TuStat')

  def set_times(self, **kwargs) -> None:
    """
    Method that allows to set the instance attribute for the step times
    of the statistical simulation.
    """
    # Check if the correct argument has been passed to the method
    if not 'sta_times' in kwargs:
      raise Exception("Error in passing arguments to this function. The statistical step times\
                      'sta_time' argument is missing.")
    # Store the times in the corresponding instance attributes
    self.sta_time =  kwargs['sta_times']

  def _activate_fields(self, event: Union[tk.Event, None] = None) -> None:
    """
    Method that activates the 'TuStat' tab plot configuration fields whenever the user
    chooses a value for the "Diagram Nr." field.
    These fields are first cleared out of any previous value and then populated accordingly.
    Users can only choose among the available values as the combobox fields are set as
    "read-only".
    """
    # Clear out the previously set values
    self.slice.cbx.set('')
    self.time.cbx.set('')
    self.n_intervals.cbx.set('')
    self.distribution.cbx.set('')

    # Set all the fields states as read-only
    self.slice.cbx['state'] = "readonly"
    self.time.cbx['state'] = "readonly"
    self.n_intervals.cbx['state'] = "readonly"
    self.distribution.cbx['state'] = "readonly"

    # Set the available values for the fields, given the information extracted from input files
    self.slice.cbx['values'] = tuple(self.slice_settings)
    self.time.cbx['values'] = tuple(self.sta_time)
    self.n_intervals.cbx['values'] = tuple([i for i in range(2, 101)])
    self.distribution.cbx['values'] = tuple(['Fractional frequency', 'Probabilistic density'])

    # Show the button for running the plot executable
    self.run_button.grid(column=1, row=8, sticky='e')

  def _are_all_fields_set(self, event: Union[tk.Event, None] = None) -> None:
    """
    Method called whenever a combobox field is set for checking if all the other fields
    have been set. If so, the button for running the TuStat executable is enabled.
    """
    # Check if all the fields have been set
    if self.slice.is_set and self.time.is_set and self.n_intervals.is_set and self.distribution.is_set:
      # Activate the button
      self.run_button.configure(state=tk.ACTIVE)
    else:
      # Disable the button
      self.run_button.configure(state=tk.DISABLED)

  def _build_configuration_fields(self, config_area: ttk.LabelFrame) -> None:
    """
    Method that builds the fields, in terms of the widgets, enabling the user to
    configure the quantities to plot for a 'TuStat' case. This method overrides
    the one already present in the 'TabContentBuilder' superclass, thus providing
    the specific implementation of the widgets for the frame provided as input.
    """
    # Build the "Diagram Nr." setup made of a label and a combobox
    self.diagram = LabelledCombobox(config_area, 0, "Diagram Nr.: ", self.gui_config.sta_numVSdescription.values())
    # Build the "Slice" setup made of a label and a combobox, disabled until the "Diagram Nr." field is undefined
    self.slice = LabelledCombobox(config_area, 1, "Slice: ", cbx_list=list(), state=tk.DISABLED)
    # Build the "Time" setup made of a label and a combobox, disabled until the "Diagram Nr." field is undefined
    self.time = LabelledCombobox(config_area, 2, "Time: ", cbx_list=list(), state=tk.DISABLED)
    # Build the "Number of intervals" setup made of a label and a combobox, disabled until
    # the "Diagram Nr." field is undefined
    self.n_intervals = LabelledCombobox(config_area, 3, "Number of intervals: ", cbx_list=list(), state=tk.DISABLED)
    # Build the "Type of distribution" setup made of a label and a combobox, disabled until
    # the "Diagram Nr." field is undefined
    self.distribution = LabelledCombobox(config_area, 4, "Type of distribution: ", cbx_list=list(), state=tk.DISABLED)

    # Bind the activation of all the configuration fields to the "Diagram Nr." field item selection
    self.diagram.cbx.bind('<<IsSet>>', func=lambda event: self._activate_fields())

    # Bind the activation of the run button to the selection of all the configuration fields
    self.slice.cbx.bind('<<IsSet>>', self._are_all_fields_set)
    self.time.cbx.bind('<<IsSet>>', self._are_all_fields_set)
    self.n_intervals.cbx.bind('<<IsSet>>', self._are_all_fields_set)
    self.distribution.cbx.bind('<<IsSet>>', self._are_all_fields_set)


if __name__ == "__main__":
  # Instantiate the root window
  root: tk.Tk = tk.Tk()
  # Set the theme to use
  set_theme("light")

  # Instantiate a notebook
  tabControl: ttk.Notebook = ttk.Notebook(root)
  tabControl.pack(fill='both', expand=True)
  # Instantiate the GuiPlotFieldsConfigurator class providing the values for filling the fields
  guiConfig: GuiPlotFieldsConfigurator = GuiPlotFieldsConfigurator.init_GuiPlotFieldsConfigurator()

  # Instatiate a TabBuilder object holding the tabs
  tab1: TuPlotTabContentBuilder = TuPlotTabContentBuilder(
     container=tabControl, tab_name="Tab 1", state='normal', guiConfig=guiConfig)
  tab1.set_slice_list(["Slice 1", "Slice 2", "Slice 3"])
  tab2: TuStatTabContentBuilder = TuStatTabContentBuilder(
    container=tabControl, tab_name="Tab 2", state='normal', guiConfig=guiConfig)
  tab2.set_slice_list(["Slice 1", "Slice 2"])

  # tabControl.tab(tab1, state=tk.DISABLED)

  root.mainloop()