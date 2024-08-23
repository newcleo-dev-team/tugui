from enum import Enum
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Union


class FieldType(Enum):
  """
  Enumeration storing the different types for plot settings fields:
  . type1 --> Kn
  . type2 --> Time
  . type3 --> Slice
  """
  type1: str = "Kn"
  type2: str = "Time"
  type3: str = "Slice"

class GroupType(Enum):
  """
  Enumeration storing the different groups for plots:
  . group1 --> function of radius
  . group2 --> function of time
  . group2A --> function of time (integral quantities)
  . group3 --> function of axial coordinate
  """
  group1: str = "Radius"
  group2: str = "Time"
  group2A: str = "TimeIntegral"
  group3: str = "Axial"


class LabelledCombobox():
  """
  Class that provides a field for setting one of the configuration options in the GUI in terms of:
  . a label: providing a description of the option
  . a combobox: providing a mean for choosing among different alternative values
  """
  def __init__(self, container: ttk.Frame, row_index: int, label_text: str,
               cbx_list: List[str], state: str = 'readonly') -> None:
    """
    Build an instance of the 'LabelledCombobox' class that provides the content of a
    configuration option. It receives as parameters:
    . container: a frame object to which this instance is added
    . row_index: an integer indicating the row index of the container grid where the
      built widgets are added
    . label_text: a descriptive string for the option field to setup
    . cbx_list: a list of values for the combobox to choose among
    . state: a string describing the combobox state, which defaults to 'readonly'
    """
    # Put a descriptive label
    self.label: ttk.Label = ttk.Label(container, text=label_text)
    self.label.grid(column=0, row=row_index, sticky='w')

    # Declare a variable holding the choosen value from the combobox field
    self.var: tk.StringVar = tk.StringVar()
    # Instantiate the combobox
    self.cbx: ttk.Combobox = ttk.Combobox(container, textvariable=self.var, state=state, values=tuple(cbx_list))
    # Put the combobox field into the frame
    self.cbx.grid(column=1, row=row_index, sticky='ew')

    # Declare a variable stating if the combobox has been set
    self.is_set: bool = False
    # Update the index indicating the row where to add additional widgets
    self.row_next: int = row_index + 1

    # Bind the selection of a value of the combobox to the execution of a method storing its value
    self.cbx.bind('<<ComboboxSelected>>', self.store_selected)

    # Add an X-Y padding to all the widgets herein defined
    self.label.grid_configure(padx=5, pady=2)
    self.cbx.grid_configure(padx=5, pady=2)

  def destroy_fields(self):
    """
    Method for destroying all the widgets declared with this class instance.
    """
    self.label.destroy()
    self.cbx.destroy()

  def store_selected(self, event=None):
    """
    Method called whenever the user select a value from the combobox. It stores the value
    in an instance variable.
    """
    print("Store value: ", self.cbx.get())
    self.cbx_selected_value = self.cbx.get()
    # Store a flag stating the combobox has been set
    self.is_set = True
    self.cbx.event_generate("<<IsSet>>")


class PlotSettingsField_2():
  """
  Class that provides the fields for setting the 'start' and 'end' time values options
  in the GUI for plots as function of the time. This fields, for both 'start' and 'end'
  times are defined in terms of the following widgets:
  . a label: providing a description of the option
  . a combobox: providing a mean for choosing among different alternative values
  """
  def __init__(self, container: ttk.Frame, row_index: int,
               cbx_list: List[str]) -> None:
    """
    Build an instance of the 'PlotSettingsField_2' class that provides the means for
    configuring the 'start' and 'end' time values options in the GUI for plots as
    function of the time. It receives as parameters:
    . container: a frame object to which this instance is added
    . row_index: an integer indicating the row index of the container grid starting
      from which the built widgets are added
    . cbx_list: a list of values for the comboboxes to choose among
    """
    # Put a descriptive label
    self.label: ttk.Label = ttk.Label(container, text="Time axis (h s ms): ")
    self.label.grid(column=0, row=row_index, sticky='w')

    # Add the configuration field for the start time
    self.start_time: LabelledCombobox = LabelledCombobox(container, row_index+1, "Start: ", cbx_list)
    # Add the configuration field for the end time (same values except for the first)
    self.end_time: LabelledCombobox = LabelledCombobox(container, row_index+2, "End: ", cbx_list[1:])
    # Update the index indicating the row where to add additional widgets
    self.row_next: int = row_index + 3
    # Bind the selection of the time values to the check for their consistency
    self.start_time.cbx.bind('<<ComboboxSelected>>', func=lambda event: self.check_time_consistency())
    self.end_time.cbx.bind('<<ComboboxSelected>>', func=lambda event: self.check_time_consistency())

    # Add an X-Y padding to the label widget herein defined
    self.label.grid_configure(padx=5, pady=2)

  def check_time_consistency(self) -> None:
    """
    Method called for checking that the value of the end time is greater than the one of
    the start time.
    """
    # Perform check only if both time combobox values have been set
    if self.start_time.cbx.current() >= 0 and self.end_time.cbx.current() >= 0:
      # Check if the end time combobox value is lesser than the start time combobox one
      if self.end_time.cbx.current() < self.start_time.cbx.current():
        # Clear the end time field
        self.end_time.cbx.set('')
        # Raise an exception
        raise Exception("Error: the end time must be greater than the start time")
      else:
        # Store the selected values
        self.time1 = self.start_time.cbx.get()
        self.time2 = self.end_time.cbx.get()
        # Store a flag stating the comboboxes have been set
        self.is_set = True

  def destroy_fields(self) -> None:
    """
    Method for destroying all the widgets declared with this class instance.
    """
    self.label.destroy()
    self.start_time.destroy_fields()
    self.end_time.destroy_fields()


class PlotSettingsListBox():
  """
  Class that provides the fields for selecting one or more values from a given list.
  This functionality relies on the following widgets:
  . a label: providing a description of the option
  . a listbox: providing a mean for choosing one or more values among different
    alternative values. This widget also presents a vertical scrollbar to help the
    inspection of the available values.
  """
  def __init__(self, container: ttk.Frame, label_text: str,
               choices: Union[List[str], None], row_index: int) -> None:
    """
    Build an instance of the 'PlotSettingsListBox' class that provides the means for
    selecting one or more values from a given list. It receives as parameters:
    . container: a frame object to which this instance is added
    . label_text: a descriptive string for the option field to setup
    . choices: a list of values for the listbox to choose among
    . row_index: an integer indicating the row index of the container grid starting
      from which the built widgets are added
    """
    # Put a descriptive label
    self.label: ttk.Label = ttk.Label(container, text=label_text)
    self.label.grid(column=0, row=row_index, sticky='w')

    # Declare a variable holding the listbox possible choices, provided as input
    self.choicesvar: tk.StringVar = tk.StringVar(value=choices)
    # Instantiate the listbox
    self.choice_lb: tk.Listbox = tk.Listbox(
      container, listvariable=self.choicesvar, selectmode=tk.EXTENDED, exportselection=False)
    # Put the listbox field into the frame
    self.choice_lb.grid(column=0, row=row_index+1, sticky='ew')
    # Configure the listbox so that it spans two columns
    self.choice_lb.grid(columnspan=2)

    # Create a vertical scrollbar for the listbox
    scrollbar = ttk.Scrollbar(container, orient= 'vertical')
    scrollbar.grid(column=1, row=row_index+1, sticky='nse')
    # Configure the scrollbar
    scrollbar.configure(command=self.choice_lb.yview)
    # Configure the listbox with the scrollbar
    self.choice_lb.configure(yscrollcommand=scrollbar.set)

    # Bind the selection of the listbox items event to a function call that stores the list of items
    self.choice_lb.bind("<<ListboxSelect>>", self.store_selected)

    # Add an X-Y padding to all the widgets herein defined
    self.label.grid_configure(padx=5, pady=2)
    self.choice_lb.grid_configure(padx=5, pady=2)

    # Update the index indicating the row where to add additional widgets
    self.row_next: int = row_index + 2

  def destroy_fields(self) -> None:
    """
    Method for destroying all the widgets declared with this class instance.
    """
    self.label.destroy()
    self.choice_lb.destroy()

  def store_selected(self, event: tk.Event = None) -> None:
    """
    Method called whenever the user select one or more values from the listbox. It stores the values
    as a list in an instance variable.
    """
    # Get the indices of the currently selected items
    indexes = self.choice_lb.curselection()
    # Declare a list holding the values to store, based on the selection
    self.lb_selected_values = list()
    # Loop over all the indexes
    for i in indexes:
      # Fill the list of selected values of the listbox
      self.lb_selected_values.append(self.choice_lb.get(i))

    # Store a flag stating the listbox items have been selected
    self.is_set = True

    print("Selected values:", self.lb_selected_values)


class PlotSettingsConfigurator():
  """
  Class that build the structure of the additional plot settings area as several rows
  containing a label and a combobox each, provided as instances of the 'LabelledCombobox'
  class, with a listbox at the end, as instance of the 'PlotSettingsListBox' class.
  The plot group choice influences the structure of the built widgets.
  """
  field1: LabelledCombobox
  field2: Union[LabelledCombobox, PlotSettingsField_2]
  field3: PlotSettingsListBox

  def __init__(self, container: ttk.Frame, group: GroupType, row_index: int) -> None:
    """
    Build an instance of the 'PlotSettingsConfigurator' class that provides the structure
    of the additional plot settings area in terms of three field with the first two being
    instances of the 'LabelledCombobox' class, whereas the last one of the
    'PlotSettingsListBox' class. Depending on the plot group, the first field can be absent,
    that is for groups '2A' and '3'. It receives as parameters:
    . container: a frame object to which this instance is added
    . group: a value of the enumeration 'GroupType' indicating the plot group
    . row_index: an integer indicating the row index of the container grid where the
      built widgets are added
    """
    # Build the structure of the additional plot settings area: it is made of
    # several rows containing a label and a combobox. A listbox handles the choice
    # of the plots to produce.
    # Build fields 1 and 2 depending on the plot group: field 1 can be absent for
    # groups 2A and 3.

    match group:
      case GroupType.group1:
        # Instantiate a label followed by a combobox for both field 1 and 2
        self.field1 = LabelledCombobox(container, row_index, "", [])
        self.field2 = LabelledCombobox(container, self.field1.row_next, "", [])

        # Bind each field selection to the execution of a method that checks if all fields have been set
        self.field1.cbx.bind('<<ComboboxSelected>>',
                             lambda event: self.handle_selection(container, self.field1.store_selected))
        self.field2.cbx.bind('<<ComboboxSelected>>',
                             lambda event: self.handle_selection(container, self.field2.store_selected))
      case GroupType.group2:
        # Instantiate a label followed by a combobox for field 1
        self.field1 = LabelledCombobox(container, row_index, "", [])
        # Instantiate a label followed by two label + combobox groups
        self.field2 = PlotSettingsField_2(container, self.field1.row_next, [])

        # Bind each field selection to the execution of a method that checks if all fields have been set
        self.field1.cbx.bind('<<ComboboxSelected>>',
                             lambda event: self.handle_selection(container, self.field1.store_selected))
        self.field2.start_time.cbx.bind('<<ComboboxSelected>>',
                                        lambda event: self.handle_selection(container, self.field2.check_time_consistency))
        self.field2.end_time.cbx.bind('<<ComboboxSelected>>',
                                      lambda event: self.handle_selection(container, self.field2.check_time_consistency))
      case GroupType.group2A:
        # Instantiate a label followed by two label + combobox groups
        self.field2 = PlotSettingsField_2(container, row_index, [])
        # Bind each field selection to the execution of a method that checks if all fields have been set
        self.field2.start_time.cbx.bind('<<ComboboxSelected>>',
                                        lambda event: self.handle_selection(container, self.field2.check_time_consistency))
        self.field2.end_time.cbx.bind('<<ComboboxSelected>>',
                                      lambda event: self.handle_selection(container, self.field2.check_time_consistency))
      case GroupType.group3:
        # Instantiate a label followed by a label + combobox group
        self.field2 = LabelledCombobox(container, row_index, "Time (h s ms)", [])
        # Bind each field selection to the execution of a method that checks if all fields have been set
        self.field2.cbx.bind('<<ComboboxSelected>>',
                             lambda event: self.handle_selection(container, self.field2.store_selected))
    # Instantiate a label followed by a listbox
    self.field3 = PlotSettingsListBox(container, "", [], self.field2.row_next)
    # Bind field3 selection to the execution of a method that checks if all fields have been set
    self.field3.choice_lb.bind('<<ListboxSelect>>',
                               lambda event: self.handle_selection(container, self.field3.store_selected))

    # Store the group value
    self.group: GroupType = group

    # Get from the last field the index indicating the row where to add additional widgets
    self.row_next: int = self.field3.row_next
    print("BUTTON ROW", self.row_next)

  def configure_fields(self,
                       field1_lbl: str = None, field1_cbx: List[str] = None,
                       field2_lbl: str = "", field2_cbx: List[str] = list(),
                       field3_lbl: str = "", field3_lbx: List[str] = list()) -> None:
    """
    Method for configuring all the widgets declared within this class instance.
    """
    # Configure field 1 only if the group is not 2A or 3
    if not (self.group == GroupType.group2A or self.group == GroupType.group3):
      self.field1.label.configure(text=field1_lbl)
      self.field1.cbx.configure(values=field1_cbx)
    # Configure field 2 label only if the group is not 2 or 2A
    if not (self.group == GroupType.group2 or self.group == GroupType.group2A):
      self.field2.label.configure(text=field2_lbl)
      self.field2.cbx.configure(values=field2_cbx)
    else:
      # Case 2/2A: set the two combobox lists
      self.field2.start_time.cbx.configure(values=field2_cbx)
      self.field2.end_time.cbx.configure(values=field2_cbx[1:])
    # Configure the remaining field
    self.field3.label.configure(text=field3_lbl)
    self.field3.choicesvar.set(field3_lbx)

  def is_everything_set(self, container: ttk.Frame) -> None:
    """
    Method that checks if every field has been set up. If so, it generates a
    virtual event, in the container frame, representing this condition.
    """
    # Check if this instance has declared field1
    if hasattr(self, 'field1'):
      # Check if all the fields are set
      if self.field1.is_set and self.field2.is_set and self.field3.is_set:
        # Generate the virtual event in the container frame
        container.event_generate('<<PlotSettingsSet>>')
    else:
      # Check if the available fields are set
      if self.field2.is_set and self.field3.is_set:
        # Generate the virtual event in the container frame
        container.event_generate('<<PlotSettingsSet>>')

  def handle_selection(self, container: ttk.Frame, set_field: Callable) -> None:
    """
    Method called whenever an event involving the set up of the value either of a combobox
    or of a listbox happens.
    It receives a generic function for setting the field value of the widget that generate
    the event. It is called in order to set a widget flag stating the field has been set.
    Afterwards, a check if all fields have been set is performed.
    """
    # Call the input function for setting the field attribute
    set_field()
    # Check if this instance has declared field1
    if hasattr(self, 'field1'):
      # Check if every field have been set ony if all have declared the corresponding flag
      if hasattr(self.field1, 'is_set') and hasattr(self.field2, 'is_set') and hasattr(self.field3, 'is_set'):
        # Call the function that checks the flags value and generates an event
        self.is_everything_set(container)
    else:
      # Check if every field have been set ony if all have declared the corresponding flag
      if hasattr(self.field2, 'is_set') and hasattr(self.field3, 'is_set'):
        # Call the function that checks the flags value and generates an event
        self.is_everything_set(container)

  def destroy_fields(self) -> None:
    """
    Method for destroying all the widgets declared within this class instance.
    """
    # Destroy field 1 only if present.
    if hasattr(self, 'field1'):
      self.field1.destroy_fields()
    self.field2.destroy_fields()
    self.field3.destroy_fields()

  def set_fields_type(self, field1_type: FieldType, field2_type: FieldType,
                      field3_type: FieldType) -> None:
    """
    Method for setting the type of all the widgets declared within this class instance.
    The available types are given by the values of the 'FieldType' enumeration.
    It helps the interpretation of the fields choices when building the .inp file.
    """
    # Set the field1 type only if present
    if hasattr(self, 'field1'):
      self.field1_type = field1_type.value
    self.field2_type = field2_type.value
    self.field3_type = field3_type.value


if __name__ == "__main__":
  # Build a window
  root: tk.Tk = tk.Tk()
  # Build the main frame
  mainframe: ttk.Frame = ttk.Frame(root)
  # Place the frame into the window grid
  mainframe.grid(column=0, row=0)

  # Instantiate the class
  plot_config: PlotSettingsConfigurator = PlotSettingsConfigurator(mainframe, GroupType.group2, 0)
  plot_config.configure_fields(
    "Pippo", ["ciao", "bello"],
    "Pippo1: ", ["ciao1", "bello1"],
    "ListBox", ['ehi', 'come', 'va', 'in', 'città'])
  plot_config.set_fields_type(FieldType['type1'], FieldType['type2'], FieldType['type3'])

  ttk.Button(mainframe, command=plot_config.destroy_fields, text="DO NOT PRESS").grid(column=1, row=4)
  # plot_lb = PlotSettingsListBox(mainframe, ['ehi', 'come', 'va', 'in', 'città'], 3)

  plot_config2: PlotSettingsField_2 = PlotSettingsField_2(mainframe, 6, ['0 0 0', '1 30 100', '2 0 0', '2 25 0'])

  print(plot_config.field1_type, plot_config.field2_type, plot_config.field3_type)

  root.mainloop()