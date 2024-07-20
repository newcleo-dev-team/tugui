import tkinter as tk
import os
import re

from tkinter import PhotoImage, ttk
from tkinter import filedialog
from tkinter import messagebox
from ttkthemes import ThemedTk

from plot_builder import PlotManager, PlotFigure
from plot_settings import GroupType
from tab_builder import TuPlotTabContentBuilder, TuStatTabContentBuilder
from tu_interface import InpHandler, MicReader, StaReader, TuInp, MacReader, configure_tuplot_inp_fields, configure_tustat_inp_fields, init_DatGenerator, init_PliReader, run_plot_files_generation
from gui_configuration import init_GuiPlotFieldsConfigurator_attrs
from gui_widgets import CustomNotebook, EntryVariable, StatusBar, provide_label_image
from support import IANT
from shutil import copyfile


class TuPostProcessingGui(ThemedTk):
  """
  Class that builds a GUI for enabling the user to plot the quantities produced by
  a TU simulation. Two plot types are available:
  . the ones showing the TU quantities as function of time, radial and axial position
  . the ones coming from a statistical simulation.
  Depending on the .pli file produced by the TU simulation, both types or the TuPlot
  ones only are available.
  This class is structured by providing:
  . a menu bar
  . an entry for setting the path to the .pli file to process
  . the plot configuration area (left side) allowing users to setup what to plot
  . the plot area (right side) where the selected curves are shown
  . a status bar (bottom window) showing log messages.
  """
  def __init__(self, window_title, width, height):
    """
    App windows's constructor
    """
    # Call the superclass constructor
    super().__init__()

    # Initialize the main GUI window
    self.__initialize_gui_window(window_title, width, height)

    # Get the absolute path of the current file
    abspath = os.path.abspath(__file__)
    # Get the file directory path
    dname = os.path.dirname(abspath)
    # Change the working directory to the one where the current executed file is located
    os.chdir(dname)

    # Set the window icon
    icon = PhotoImage(file=os.path.join(os.getcwd(), "../resources/icons/tuoutgui.gif"))
    self.iconphoto(False, icon)
    # self.tk.call('wm', 'iconphoto', self._w, icon)
    # self.iconphoto(True, PhotoImage(file=os.path.join(os.getcwd(), "resources/tuoutgui.ico")))

    # Instantiate and configure the 'GuiPlotFieldsConfigurator' class in a try-except
    try:
      self.guiconfig = init_GuiPlotFieldsConfigurator_attrs()
    except Exception as e:
      # Intercept any exception produced by running the configuration logic
      messagebox.showerror("Error", type(e).__name__ + "–" + str(e))
      # Quit the application as this case represents a fatal error
      self.quit_app()
      # Propagate the caught exception
      raise e

    # Build the menu bar
    self.create_menu()

    # Set the initial directory to the current working directory
    self.initial_dir = os.getcwd()

    # Set the initial number of rows and columns and how much they are resized
    self.grid_rowconfigure((0,2), weight=0)
    self.grid_rowconfigure(1, weight=3)
    self.grid_columnconfigure((0,1), weight=1)

    # tk.set_appearance_mode("Dark")
    # TODO: check how to set a dark-mode
    s = ttk.Style()

    self.configure(background='#F6F4F2')
    # s.configure('TFrame', background='black')
    # s.configure('TLabel', background='black', foreground='white')
    # s.configure('TButton', background='black', foreground='black', highlightbackground='black', highlightcolor='black')
    # s.map('TButton',
    #     foreground=[('disabled', 'yellow'),
    #                 ('pressed', 'red'),
    #                 ('active', 'black')],
    #     background=[('disabled', 'magenta'),
    #                 ('pressed', '!focus', 'cyan'),
    #                 ('active', 'black')],
    #     highlightcolor=[('focus', 'black'),
    #                     ('!focus', 'black')],
    #     relief=[('pressed', 'groove'),
    #             ('!pressed', 'ridge')])

    ############################################
    # Build the upper section of the main window
    ############################################
    # Instantiate a Frame object holding the .pli setting section
    mainframe = ttk.Frame(self)
    mainframe.grid(column=0, row=0, sticky='ew')

    # Instantiate a label for the .pli file entry
    ttk.Label(mainframe, text="Path to the .pli input file").grid(column=0, row=0, sticky='ew')
    # Instantiate the field holding the path to the .pli input file
    self.pli_entry = EntryVariable(mainframe, 50, col=1, row=0, end="pli")
    # Put a button next the the entry for allowing the selection of the .pli file to open
    ttk.Button(mainframe, # width = 80,
               text="Choose file",
               command=lambda: self.select_file_and_fill_entry(
                 self.pli_entry.entry, "Input .pli file", "pli")).grid(column=2, row=0, sticky='ew')

    # Instantiate a Frame object holding the logos
    logo_frame = ttk.Frame(self)
    logo_frame.grid(column=1, row=0, sticky='nse')
    # Add newcleo and JRC logos
    newcleo_logo = provide_label_image(logo_frame, os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/newcleologo.png"))
    newcleo_logo.grid(column=0, row=0, sticky='nsew')
    jrc_logo = provide_label_image(logo_frame, os.path.join(os.path.abspath(os.path.dirname(__file__)), "../resources/icons/jrclogo.png"))
    jrc_logo.grid(column=1, row=0, sticky='nsew')

    ###############################################################################
    # Build the plot configuration area for the two types of plot (TUPlot e TUStat)
    ###############################################################################
    self.build_tabs_area()

    # Add a status bar to the bottom of the window
    self.status_bar = StatusBar(self)
    self.status_bar.grid(column=0, row=2, columnspan=2)

    # Add a padding for each widget in the top section frame
    for child in mainframe.winfo_children():
      child.grid_configure(padx=5, pady=5)

    ####################################################
    # Declare events binding to call to instance methods
    ####################################################
    # Bind Ctrl+N to the request of resetting the post-processing window
    self.bind("<Control-n>", func=self.reset_main_window)
    # Bind Ctrl+O to the request of opening a new .pli input file
    self.bind("<Control-o>", func=self.open_pli_file)
    # Bind Ctrl+W to the request of selecting the output folder
    self.bind("<Control-w>", func=self.select_output_folder)
    # Bind Ctrl+Q to the request of quitting the application
    self.bind("<Control-q>", func=self.quit_app)
    # Bind the entry "FocusOut" event to the method that retrieves the information from the input .pli file
    self.pli_entry.entry.bind("<FocusOut>", func=lambda event: self.retrieve_simulation_info())
    # Bind the activation of the plot tabs to a valid set of the .pli entry field. If this file shows a value of 1
    # for the ISTATI field, both TuPlot and TuStat areas are enabled. If not, only the TuPlot one is available.
    # In the first case, the "ActivateAllTabs" event activates both tabs; in the second case, the "ActivateTuPlotTab"
    # event activate only the TuPlot one.
    self.bind('<<ActivateAllTabs>>', func=lambda event: self.activate_all_tabs())
    self.bind('<<ActivateTuPlotTab>>', func=lambda event: self.activate_tuplot_area())

    # Bind the <<Reload>> virtual event to the clearing of all the settings and plots
    # thus rebuilding the plot settings fields options.
    self.bind('<<Reload>>', func=lambda event: self.build_tabs_area())

    # Bind the <<InpLoaded>> virtual event to the plot creation
    self.bind('<<InpLoaded>>', func=lambda event: self.display_inp_plots())
    # Bind the <<DatPltLoaded>> virtual event to the plot creation
    self.bind('<<DatPltLoaded>>', func=lambda event: self.display_plot())

  def __initialize_gui_window(self, title, width, height):
    """
    Method that sets the GUI window title, as well as its dimensions, in terms
    of width and height. Given the screen size, the window is placed in the center
    of the screen, independently of its dimensions.
    """
    # Set the window title
    self.title(title)
    # Set the theme to use
    self.configure(theme='radiance')
    # Set the top-left coordinate of the window so that the app is placed in the screen center
    left = int(self.winfo_screenwidth() / 2 - width / 2)
    top = int(self.winfo_screenheight() / 2 - height / 2)
    # Set the window geometry
    self.geometry(f"{width}x{height}+{left}+{top}")

  def display_plot(self):
    """
    Method that enables the display-only mode for plots provided by reading
    the input .dat and .plt files.
    In case the plot configuration mode was enabled, the method changes the
    GUI layout to display only the plots and the related report.
    """
    # Destroy the objects holding the TuPlot and TuStat sections and delete
    # the corresponding instance attributes, if they are present.
    if hasattr(self, 'tabControl'):
      print("\n######### DESTROY CONFIG TABS ###########\n")
      self.tabControl.destroy()
      delattr(self, 'tabControl')

    # Clear any previously displayed plot
    if hasattr(self, 'plotTabControl'):
      print("\n######### DESTROY PREVIOUS PLOTS ###########\n")
      self.plotTabControl.destroy()
      delattr(self, 'plotTabControl')

    # Clear the input .pli entry
    self.pli_entry.entry.delete(0, tk.END)

    # Declare a style fot the CustomNotebook object so to add a bit of margin on the top
    s = ttk.Style()
    s.configure("CustomNotebook", tabmargins=[0, 5, 0, 0])
    # Instantiate the CustomNotebook object and place it into the grid
    self.plotTabControl = CustomNotebook(self, style='CustomNotebook')
    # The tab can span 2 columns so to overlap with the following button
    self.plotTabControl.grid(column=0, row=1, columnspan=2, sticky='nsew')

    # Build a diagram for each plot of the loaded .dat and .plt files
    for i in range(0, len(self.loaded_dat_files)):
      # Build the plot frame where the plots are shown
      plot_figure = PlotFigure(self.plotTabControl)
      # Destroy the report area as no input report is provided
      plot_figure.report_frame.destroy()
      # Add the just built plot frame to the notebook
      self.plotTabControl.add(plot_figure, text=f"Plot {i+1}")
      # Plot the i-th diagram
      self.plot_curves(plot_figure, self.loaded_dat_files[i], self.loaded_plt_files[i], "")

  def display_inp_plots(self):
    """
    Method that enables the display-only mode for plots provided by reading
    an input .inp file.
    In case the plot configuration mode was enabled, the method changes the
    GUI layout to display only the plots and the related report.
    """
    # Destroy the objects holding the TuPlot and TuStat sections and delete
    # the corresponding instance attributes, if they are present.
    if hasattr(self, 'tabControl'):
      print("\n######### DESTROY CONFIG TABS ###########\n")
      self.tabControl.destroy()
      delattr(self, 'tabControl')

    # Clear any previously displayed plot provided by loading an .inp file
    if hasattr(self, 'plotTabControl'):
      print("\n######### DESTROY PREVIOUS PLOTS ###########\n")
      self.plotTabControl.destroy()
      delattr(self, 'plotTabControl')

    # Clear the input .pli entry
    self.pli_entry.entry.delete(0, tk.END)

    # If the output directory has not been specified, use the .inp file folder
    if not hasattr(self, 'output_dir'):
      self.output_dir = os.path.dirname(self.loaded_inp_file)

    # Declare a style for the CustomNotebook object so to add a bit of margin on the top
    s = ttk.Style()
    s.configure("CustomNotebook", tabmargins=[0, 5, 0, 0])
    # Instantiate the CustomNotebook object and place it into the grid
    self.plotTabControl = CustomNotebook(self, style='CustomNotebook')
    # The tab can span 2 columns so to overlap with the following button
    self.plotTabControl.grid(column=0, row=1, columnspan=2, sticky='nsew')

    # Instantiate the class that read and extract the content of the .inp file
    # in order to know how many diagrams need to be produced
    inpreader = InpHandler(self.loaded_inp_file)
    # Read the loaded .inp file and extract its content
    inpreader.read_inp_file()
    # Save the content of the read .inp file into a file whose name complies with
    # what needed by the plotting executables
    self.loaded_inp_file = inpreader.save_loaded_inp()

    # Handle the TuPlot and TuStat plot cases differently
    if inpreader.diagrams_list[0].is_tuplot:
      # Get the path to the TuPlot executable
      executable_path = self.guiconfig.tuplot_path
      # Set the default name of the files the plotting executable will create
      output_files_name = "TuPlot"
    else:
      # Get the path to the TuStat executable
      executable_path = self.guiconfig.tustat_path
      # Set the default name of the files the plotting executable will create
      output_files_name = "TuStat"

    # Run the function that deals with instantiating the dataclass storing the needed
    # information for the plotting executable to be run
    inp_to_dat = init_DatGenerator(plotexec_path=executable_path,
                                   inp_path=self.loaded_inp_file,
                                   plots_num=len(inpreader.diagrams_list),
                                   cwd=self.output_dir,
                                   output_files_name=output_files_name)
    # Run the plotting executable for creating the .dat and .plt files
    run_plot_files_generation(inp_to_dat)

    # For each diagram configuration create a new PlotFigure object and plot the curves
    for i in range(0, len(inpreader.diagrams_list)):
      # Build the plot frame where the plots are shown
      plot_figure = PlotFigure(self.plotTabControl)
      # Add the just built plot frame to the notebook
      self.plotTabControl.add(plot_figure, text=f"Plot {i+1}")
      # Plot the i-th diagram
      self.plot_curves(plot_figure, inp_to_dat.dat_paths[i], inp_to_dat.plt_paths[i], inp_to_dat.out_paths[i])

  def build_tabs_area(self):
    """
    Method that builds the tabs containing the plot configuration area and the plot display one
    for both the TuPlot and the TuStat cases.
    Both tabs are built with an initial "Disabled" state, meaning that their content cannot be
    accessed by default.
    """
    # Destroy the notebook holding the plot figure, if any is present
    if hasattr(self, 'plotTabControl'):
      self.plotTabControl.destroy()
      # Delete the attribute
      delattr(self, 'plotTabControl')

    # Change the style of the Notebook object for positioning the tabs on the bottom-left corner
    # tab_style = ttk.Style()
    # tab_style.configure('TNotebook', tabposition='nw')
    # Instatiate a Notebook object holding all the tabs
    self.tabControl = ttk.Notebook(self)
    # Position the notebook into the main window grid
    self.tabControl.grid(column=0, row=1, sticky="nsew", columnspan=2)
    # Build the content of each tab frame by instantiating the class TabContentBuilder
    self.tuplot_tab = TuPlotTabContentBuilder(
        self.tabControl, tab_name="TU Plot", state=tk.DISABLED, guiConfig=self.guiconfig)
    self.tustat_tab = TuStatTabContentBuilder(
        self.tabControl, tab_name="TU Stat", state=tk.DISABLED, guiConfig=self.guiconfig)

  def retrieve_simulation_info(self):
    """
    Method that extract all the needed information from the .pli input file. Given the
    paths to the .mac, .mic, .sta, .sti files therein present, the method provides the
    macro and micro steps of the TU simulation, the number of axial positions (slices),
    the times of the statistical simulation, if present.
    Given the ISTATI value in the .pli file, a different event is generated:
    . if ISTATI = 1, the "ActivateAllTabs" event is generated to enable both TuPlot and
      TuStat tabs
    . if ISTATI = 0, the "ActivateTuPlotTab" event is generated to enable the TuPlot tab
      only.
    """
    # Return immediately if no value for the .pli entry is present
    if self.pli_entry.var.get() == "": return
    # In case of plot display-only mode, generate the event for rebuilding the configuration
    # and the plot areas
    if hasattr(self, 'plotTabControl'):
      self.event_generate('<<Reload>>')
    # In case a previous .pli file has already been opened, check if the path of the entry
    # has changed.
    if hasattr(self, 'plireader') and self.plireader.pli_path != self.pli_entry.var.get():
      # The path has changed, hence generate a virtual event for clearing any previously
      # settings or plot, thus reloading all the fields.
      self.event_generate('<<Reload>>')

    # Instantiate the PliReader class for retrieving info from the .pli file
    try:
      # Extract the information from the .pli file and instantiate the 'PliReader' class
      self.plireader = init_PliReader(self.pli_entry.var.get())
      print("Path to the .pli file: " + self.plireader.pli_path)

      # Instantiate the MacReader class
      self.macreader = MacReader(
        os.path.dirname(self.plireader.pli_path) + os.sep + self.plireader.mac_path,
        self.plireader.axial_steps)
      # Extract the macro step time values
      (h, s, ms) = self.macreader.extract_xtime_hsms(int(self.plireader.mac_recordLength))
      # Join the values of the 3 arrays into a list of strings
      self.macro_time = list()
      for (i, j, k) in zip(*list((h, s, ms))):
        self.macro_time.append(str(i) + " " + str(j) + " " + str(k))

      # Instantiate the MicReader class
      self.micreader = MicReader(os.path.dirname(self.plireader.pli_path) + os.sep + self.plireader.mic_path)
      # Extract the microstep time values
      (h, s, ms) = self.micreader.extract_time_hsms(int(self.plireader.mic_recordLength))
      # Join the values of the 3 arrays into a list of strings
      self.micro_time = list()
      for (i, j, k) in zip(*list((h, s, ms))):
        self.micro_time.append(str(i) + " " + str(j) + " " + str(k))

      # Buid a list of slice indexes based on the number of slices read from the .pli file
      self.slice_settings = list()
      for i in range(self.plireader.axial_steps):
        self.slice_settings.append(str(i+1) + " Slice")

      print("ISTATI = ", self.plireader.opt_dict['ISTATI'])
      # Check if a statistical simulation is present as well, based on the ISTATI value
      if self.plireader.opt_dict['ISTATI'] == str(1):
        # Instantiate the StaReader class
        self.stareader = StaReader(
          os.path.dirname(self.plireader.pli_path) + os.sep + self.plireader.sta_path,
          int(self.plireader.opt_dict['IBYTE']))
        # Extract the time values of the statistical simulation from the .sta file
        (h, s, ms) = self.stareader.extract_time_hsms(
          record_length=int(self.plireader.sta_recordLength),
          axial_steps=self.plireader.axial_steps - 1,
          sta_dataset_length=int(self.plireader.sta_dataset))
        # Join the values of the 3 arrays into a list of strings
        self.sta_times = list()
        for (i, j, k) in zip(*list((h, s, ms))):
          self.sta_times.append(str(i) + " " + str(j) + " " + str(k))
        # Generate the event for activating both TuPlot and TuStat tabs
        print("Generating ActivateAllTabs event...")
        self.event_generate('<<ActivateAllTabs>>')
      else:
        print("Generating ActivateTuPlotTab event...")
        # Generate the event for activating the TuPlot tab only
        self.event_generate('<<ActivateTuPlotTab>>')
    except Exception as e:
      # Intercept any exception produced by instantiating the PliReader class and by
      # extracting from it and from the other files the available information. A
      # pop-up box is produced showing the error message
      messagebox.showerror("Error", type(e).__name__ + "–" + str(e))

  def activate_all_tabs(self):
    """
    Method that activates both the TuPlot and the TuStat tabs by calling the
    corresponding methods.
    """
    self.activate_tuplot_area()
    self.activate_tustat_area()

  def activate_tustat_area(self):
    """
    Method that activates the TuStat tab by changing the state attribute of the
    corresponding tab object.
    Afterwards, it activates the "Diagram Nr." field and sets the lists of available
    slices and times with values read from the .sta file, while passing the function
    to be run when the button in the tab area is pressed.
    """
    print("Activating the TuStat tab...")
    self.tabControl.tab(self.tustat_tab, state=tk.NORMAL)
    # Activate the "Diagram Nr." field of the active tab
    print("Setting Diagram Nr. field state for TuStat...")
    self.tustat_tab.diagram.cbx.configure(state='readonly')

    # Set the list of slice names for the TuStat tab
    self.tustat_tab.set_slice_list(self.slice_settings)
    # Set the list providing the times of the statistical simulation
    self.tustat_tab.set_times(sta_times=self.sta_times)
    # Pass the herein-defined method to call whenever the "Run" button of the TuStat tab is pressed
    self.tustat_tab.run_plot(self.run_tuStat)

  def activate_tuplot_area(self):
    """
    Method that activates the TuPlot tab by changing the state attribute of the
    corresponding tab object.
    Afterwards, it activates the "Group" field and sets the lists of available
    slices and times with values read from the .mac/.mic files, while passing
    the function to be run when the button in the tab area is pressed.
    """
    print("Activating the TuPlot tab...")
    self.tabControl.tab(self.tuplot_tab, state=tk.NORMAL)

    # Activate the group field of the active tabs
    print("Setting Group field state for TuPlot...")
    self.tuplot_tab.group.cbx.configure(state='readonly')
    # Select the TuPlot tab in order to show its content
    self.tabControl.select(self.tuplot_tab)

    # Set the list of slice names for the TuPlot tab
    self.tuplot_tab.set_slice_list(self.slice_settings)
    # Set the lists providing the macro and micro time
    self.tuplot_tab.set_times(macro_time=self.macro_time, micro_time=self.micro_time)
    # Pass the herein-defined method to call whenever the "Run" button of the TuPlot object is pressed
    self.tuplot_tab.run_plot(self.run_tuPlot)

  def run_tuPlot(self):
    """
    Method that runs the TuPlot executable by passing the required .inp file.
    This file is first built up based on the user's choices made in the plot
    configuration area.
    After producing the output .dat and .plt files, these files are passed to
    the method that handles the curves plot.
    """
    # Remove focus from the run button by assigning it to the root window
    self.focus_set()

    try:
      # Get the index corresponding to the IDGA option selected by users
      idga_indx = self.guiconfig.idgaVSi[self.tuplot_tab.type_var.get()]

      # Instantiate the class dealing with the .inp file generation based on the made choices
      # inp_generator = TuPlotInpGenerator(self.plireader.pli_path)
      # Build a dictionary of the needed information for building the .inp file by providing
      # default values for each entry.
      inp_info = {
        "PLI": os.path.basename(self.plireader.pli_path).split(os.sep)[-1],
        "IDNF": self.tuplot_tab.number_var.get().split(' ')[0],
        "IDGA": str(idga_indx),
        "NKN": str(len(self.tuplot_tab.plt_sett_cfg.field3.lb_selected_values)),
        "IANT1": "N",
        "IANT2": "F",
        "IANT3": "N",
        "KN": "1",
        "NLSUCH": "1",
        "TIME": "0 0 0",
        "NMAS": "0",
        "IKON": "E"
      }

      # Overwrite the default entry for the temperature distribution if plot 113
      if hasattr(self.tuplot_tab, 'iant'):
        if self.tuplot_tab.iant == IANT.IANT_1.description:
          # TODO check why the manual says this field shoud be 'Y', but actually the executable fails
          inp_info["IANT1"] = "N"
        elif self.tuplot_tab.iant == IANT.IANT_2.description:
          # Overwrite the default entry for the radial stresses, if plot 102-108
          if hasattr(self.tuplot_tab, 'iant_entry'):
            if self.tuplot_tab.iant_entry.cbx.current() == 0:
              inp_info["IANT2"] = "C"

      # If the plot type (IDGA) is 1, put the list of selected Kn-s in the dictionary
      if idga_indx == 1:
        # Get the list of strings identifying the chosen Kn-s
        kn_list = self.tuplot_tab.plt_sett_cfg.field3.lb_selected_values
        # Extract the Kn numbers only if the list is not empty
        if len(kn_list) > 0:
          # Get the list of Kn numbers
          inp_info["KN"] = " ".join([re.findall(r'\d+', item)[0] for item in kn_list])
      else:
        # Get the value of selected Kn from the corresponding field
        if hasattr(self.tuplot_tab.plt_sett_cfg, 'field1') and self.tuplot_tab.plt_sett_cfg.field1_type == "Kn":
          print("TYPE FIELD1", self.tuplot_tab.plt_sett_cfg.field1_type)
          inp_info["KN"] = re.findall(r'\d+', self.tuplot_tab.plt_sett_cfg.field1.cbx_selected_value)[0]
        elif self.tuplot_tab.plt_sett_cfg.field2_type == "Kn":
          inp_info["KN"] = re.findall(r'\d+', self.tuplot_tab.plt_sett_cfg.field2.cbx_selected_value)[0]

      # Overwrite the default entry for the NLSUCH item
      if idga_indx == 3:
        # Get the number of selected slices
        slice_list = self.tuplot_tab.plt_sett_cfg.field3.lb_selected_values
        # Extract the slice numbers only if the list is not empty
        if len(slice_list) > 0:
          # Get the list of Kn numbers
          inp_info["NLSUCH"] = " ".join([re.findall(r'\d+', item)[0] for item in slice_list])
      else:
        # Get the value of selected slice from the corresponding field
        if hasattr(self.tuplot_tab.plt_sett_cfg, 'field1') and self.tuplot_tab.plt_sett_cfg.field1_type == "Slice":
          inp_info["NLSUCH"] = re.findall(r'\d+', self.tuplot_tab.plt_sett_cfg.field1.cbx_selected_value)[0]
        elif self.tuplot_tab.plt_sett_cfg.field2_type == "Slice":
          inp_info["NLSUCH"] = re.findall(r'\d+', self.tuplot_tab.plt_sett_cfg.field2.cbx_selected_value)[0]

      # Overwrite the default TIME (IASTUN/IASEC/FAMILY) entries on the basis of the selected time(s)
      if idga_indx == 1 or idga_indx == 3:
        # Curves at a specific time instant, i.e. one time for plot type 1 (different Kn-s) and 3 (different slices)
        if self.tuplot_tab.plt_sett_cfg.group == GroupType.group1 or self.tuplot_tab.plt_sett_cfg.group == GroupType.group3:
          # Only one time for group 1 (Radius) and 3 (Axial)
          # Get the time from field2
          inp_info["TIME"] = self.tuplot_tab.plt_sett_cfg.field2.cbx_selected_value
        elif self.tuplot_tab.plt_sett_cfg.group == GroupType.group2 or self.tuplot_tab.plt_sett_cfg.group == GroupType.group2A:
          # Start and end times for group 2 (Time) and 2A (TimeIntegral)
          # Get the start/end times from field2
          inp_info["TIME"] = "\n".join([self.tuplot_tab.plt_sett_cfg.field2.time1, self.tuplot_tab.plt_sett_cfg.field2.time2])
      elif idga_indx == 2:
        # Curves for different time instants, list of times for plot type 1 (different Kn-s) and 3 (different slices)
        if self.tuplot_tab.plt_sett_cfg.group == GroupType.group1 or self.tuplot_tab.plt_sett_cfg.group == GroupType.group3:
          # Get the list of selected time instants from field3
          times = self.tuplot_tab.plt_sett_cfg.field3.lb_selected_values
          inp_info["TIME"] = "\n".join(i for i in times)

      # Build and configure the 'TuInp' dataclass for storing the plot configuration
      tuplot_inp = configure_tuplot_inp_fields(inp_info)

      # Get the 'PlotFigure' instance from the currently active tab of the plots notebook
      active_plotFigure = self.tuplot_tab.get_active_plotFigure()

      # Save the plot configuration .inp file and run the plotting executable to produce
      # the output files needed to plot the current diagram
      self.handle_plot_production(tuplot_inp, 'TuPlot', self.guiconfig.tuplot_path, active_plotFigure)

    except Exception as e:
      # Intercept any exception produced while generating the .inp file or while running the tuplotgui executable interface and
      # show a pop-up error message
      messagebox.showerror("Error", type(e).__name__ + "–" + str(e))
      raise Exception(e)

  def run_tuStat(self):
    """
    Method that runs the TuStat executable by passing the required .inp file.
    This file is first built up based on the user's choices made in the plot
    configuration area.
    After producing the output .dat and .plt files, these files are passed to
    the method that handles the curves plot.
    """
    # Remove focus from the run button by assigning it to the root window
    self.focus_set()

    try:
      print("Running TuStat...")
      # Instantiate the class dealing with the .inp file generation based on the made choices
      # inp_generator = TuStatInpGenerator(self.plireader.pli_path)
      # Build a dictionary of the needed information for building the .inp file by providing
      # default values for each entry.
      inp_info = {
        "PLI": os.path.basename(self.plireader.pli_path).split(os.sep)[-1],
        "DIAGNR": self.tustat_tab.diagram.cbx_selected_value.split(' ')[0],
        "NAXIAL": self.tustat_tab.slice.cbx_selected_value.split(' ')[0],
        "TIME": self.tustat_tab.time.cbx_selected_value,
        "INTERV": self.tustat_tab.n_intervals.cbx_selected_value,
        "DISTR": "f",
        "CONTIN": "E"
      }

      # Overwrite the default entry for the type of distribution (DISTR) item, where:
      # . f - fractional frequency
      # . d - probabilistic density
      if self.tustat_tab.distribution.cbx.current() == 0:
        # Index 0 corresponds to "Fractional frequency"
        inp_info["DISTR"] = "f"
      else:
        # Index 1 corresponds to "Probabilistic density"
        inp_info["DISTR"] = "d"

      # Build and configure the 'TuInp' dataclass for storing the plot configuration
      tustat_inp = configure_tustat_inp_fields(inp_info)

      # Get the 'PlotFigure' instance from the currently active tab of the plots notebook
      active_plotFigure = self.tustat_tab.get_active_plotFigure()

      # Save the plot configuration .inp file and run the plotting executable to produce
      # the output files needed to plot the current diagram
      self.handle_plot_production(tustat_inp, 'TuStat', self.guiconfig.tustat_path, active_plotFigure)

    except Exception as e:
      # Intercept any exception produced while generating the .inp file or while running the tustatgui executable interface and
      # show a pop-up error message
      messagebox.showerror("Error", type(e).__name__ + "–" + str(e))

  def handle_plot_production(self, tuinp: TuInp, output_files_name: str, executable_path: str, active_plotFigure: PlotFigure):
    """
    Method that handles all the operations for displaying the diagrams on the plotting area of the main window.
    In particular, we have that:
    . given the 'TuInp' dataclass instance, writes the .inp file from the content of the dataclass;
    . given the path to the plotting executable, it runs it by passing the built .inp file;
    . given the resulting output files, the plot figure is produced on the given 'PlotFigure' instance.
    """
    # Instantiate the 'TuInpHandler' class by providing the path to the .inp file, in the same
    # folder of the .pli file
    inp_path = os.path.join(os.path.dirname(self.plireader.pli_path), output_files_name + '.inp')
    inp_handler = InpHandler(inp_path)
    # Write the .inp file into the .pli file folder
    inp_handler.save_inp_file([tuinp])

    # Store the .inp filename
    self.inp_filename = inp_path

    # Run the function that deals with instantiating the dataclass storing the needed
    # information for the plotting executable to be run
    inp_to_dat = init_DatGenerator(plotexec_path=executable_path,
                                   inp_path=inp_path,
                                   plots_num=1,
                                   cwd=self.output_dir,
                                   output_files_name=output_files_name)
    # Run the plotting executable for creating the .dat and .plt files
    run_plot_files_generation(inp_to_dat)

    # Store the currently .dat and .plt output files (first element in the
    # corresponding lists as only one plot is handled here)
    self.active_dat_file = inp_to_dat.dat_paths[0]
    self.active_plt_file = inp_to_dat.plt_paths[0]

    # Generate the event for turning off the toolbar buttons, thus resetting their states
    active_plotFigure.event_generate('<<DeselectButtons>>')
    # Extract the data from the produced .dat and .plt files and plot the selected curves
    # onto the currently active tab figure --> only 1 .dat and .plt file is considered
    self.plot_curves(active_plotFigure, self.active_dat_file, self.active_plt_file, inp_to_dat.out_paths[0])

  def plot_curves(self, plotFigure: PlotFigure, dat_file: str, plt_file: str, out_file: str):
    """
    Method that instantiate the class handling the plot functionalities:\n
    . the output .dat and .plt files are read in order to extract:\n
      - the X-Y values\n
      - the plot display information (e.g. plot title, axes names, etc.)
    . curves are plotted onto the provided PlotFigure object
    """
    try:
      # Instantiate the class handling the plot configuration
      plot_manager = PlotManager(dat_file, plt_file, out_file)
      # Configure and show the plots on the figure
      plot_manager.plot(plotFigure)
    except Exception as e:
      # Intercept any exception raised while preparing the plot figure and
      # pop-up an error message
      print(e.__cause__)
      messagebox.showerror("Error", type(e).__name__ + "–" + str(e))
      raise Exception(e)

  def open_pli_file(self, event=None):
    """
    Method for asking the user to open an input .pli file.
    """
    self.select_file_and_fill_entry(self.pli_entry.entry, "Input file", "pli")

  def select_file(self, fileToSearch: str, format: str):
    """
    Method for asking the user to select a file by opening a file selection window.
    A string representing the format of the target file is provided in order
    to enable filtering of files in folders with the correct extension.
    """
    # Declare a tuple of tuples having the file type and its extension for filtering files in folders.
    # The last one allows to show all files in folders.
    filetypes = (
      (fileToSearch, '*.' + format),
      ('All files', '*.*')
    )
    # Open a select file window by calling the corresponding Tkinter method returning the path of the
    # selected file.
    return filedialog.askopenfilename(
      title = 'Choose the file',
      initialdir = self.initial_dir,
      filetypes = filetypes)

  def select_file_and_fill_entry(self, entry: ttk.Entry, fileToSerch: str, format: str):
    """
    Method for asking the user to select a file by opening a file selection window.
    An Entry object is provided as input so that the path to the selected file is
    passed to it and showed in the GUI.
    A string representing the format of the target file is provided as well in order
    to enable filtering of files in folders with the correct extension.
    """
    # Remove focus from the run button by assigning it to the root window
    self.focus_set()

    # Open a select file window by calling the corresponding Tkinter method returning the path of the
    # selected file.
    filename = self.select_file(fileToSerch, format)

    # Do nothing if no file has been selected
    if not filename: return

    # Update the default directory of the open window to the one of the currently opened file
    self.initial_dir = os.path.dirname(filename)

    # If not already done, set the output directory to the one of the currently opened file
    if not hasattr(self, 'output_dir'):
      self.output_dir = self.initial_dir

    # Provide a message to the status bar
    self.status_bar.set_text("Selected .pli file: " + filename)

    # Delete any already present path in the given entry
    entry.delete(0, tk.END)
    # Insert the selected file path in the given entry
    entry.insert(0, filename)

    # Give focus to the entry
    entry.focus()
    # Remove focus from the entry (by passing it to the window) in order to trigger the entry
    # content validation
    self.focus()

  def select_output_folder(self, event=None):
    """
    Method for asking the user to select the output folder by opening a selection window.
    """
    # If not already done, set the output directory to the one of the currently opened file
    # or its default one
    if not hasattr(self, 'output_dir'):
      self.output_dir = self.initial_dir

    # Open a select folder window by calling the corresponding Tkinter method returning the
    # path of the selected folder.
    foldername = filedialog.askdirectory(
      title = 'Choose folder where output files should be saved',
      initialdir = self.output_dir,
      mustexist = True)

    # Do nothing if no folder has been selected
    if not foldername: return

    # Update the output directory to the one currently selected
    self.output_dir = foldername

    print("Selected output folder:", self.output_dir)

  def load_inp_file(self, event=None):
    """
    Method for asking the user to select a plot configuration .inp file to load by opening
    a file selection window.
    Once selected, the '<<InpLoaded>>' virtual event is generated to trigger the plot creation.
    """
    # Ask the user to select a plot configuration .inp file to load
    filename = self.select_file("Plot configuration file", "inp")
    # Do nothing if no .inp file has been selected
    if not filename: return

    # Store the selected file as an instance attribute
    self.loaded_inp_file = filename
    # Change the start directory for the file selection window
    self.initial_dir = os.path.dirname(filename)

    # Provide a message to the status bar
    self.status_bar.set_text("Selected .inp file: " + self.loaded_inp_file)

    # Generate the '<<InpLoaded>>' virtual event
    self.event_generate('<<InpLoaded>>')

  def load_output_files(self, event=None):
    """
    Method for asking the user to select the plot configuration files provided as a couple of
    .dat and .plt files, with the first containing the X-Y data of the curves and the second
    the information for configuring the plot figure.
    Once are both selected, the '<<DatPltLoaded>>' virtual event is generated to trigger the
    plot creation.
    """
    # Declare the list of the extensions for the plot configuration files to load
    file_extensions = ['*.dat', '*.plt']
    ftypes = [
        ('Plot configuration files', file_extensions),
        ('All files', '*'),
    ]

    # Ask the user to select the plot configuration .dat and .plt files to load
    filenames = filedialog.askopenfilenames(
      initialdir=self.initial_dir,
      title="Select the files to load",
      filetypes=ftypes)

    # Do nothing if no .dat-.plt files have been selected
    if not filenames: return

    # Store the selected files as an instance attribute
    self.loaded_dat_files = [f for f in filenames if f.endswith(".dat")]
    self.loaded_plt_files = [f for f in filenames if f.endswith(".plt")]
    # Check if both lists have the same sizes
    if len(self.loaded_dat_files) != len(self.loaded_plt_files):
      # Pop-up an error message
      messagebox.showerror("Error", "Error: there is an incoherent number of .dat and .plt files.")
      # Exit
      return

    # Change the start directory for the file selection window
    self.initial_dir = os.path.dirname(filenames[0])

    # Provide a message to the status bar
    self.status_bar.set_text("Selected .dat/.plt file from directory: " + self.initial_dir)

    # Generate the '<<InpLoaded>>' virtual event
    self.event_generate('<<DatPltLoaded>>')

  def save_file(self, fileToSave: str, format: str):
    """
    """
    # Declare a tuple of tuples having the file type and its extension for filtering files in folders.
    # The last one allows to show all files in folders.
    filetypes = (
      (fileToSave, '*.' + format),
      ('All files', '*.*')
    )
    # Open a select file window by calling the corresponding Tkinter method returning the path of the
    # selected file.
    return filedialog.asksaveasfilename(
      title = 'Choose the file',
      initialdir = self.initial_dir,
      filetypes = filetypes)

  def save_inp_file(self, event=None):
    """
    Method for asking the user to save the currently active plot configuration .inp file by opening
    a file save selection window.
    """
    # Ask the user to select a plot configuration .inp file to load
    filename = self.save_file("Plot configuration file", "inp")
    # Do nothing if no .inp file has been indicated
    if not filename: return

    # Check if the .inp file name is present
    if not hasattr(self, 'inp_filename'):
      # Pop-up an error message
      messagebox.showerror("Error", "Error: no plot configuration '.inp' file is present.")
      return

    # Copy the content of source to destination
    dest = copyfile(self.inp_filename, filename)

    # Provide a message to the status bar
    self.status_bar.set_text("Saved .inp file: " + dest)

  def save_output_files(self, event=None):
    """
    Method for asking the user to save the currently active plot configuration .inp file by opening
    a file save selection window.
    """
    # Ask the user to select a plot configuration .inp file to load
    filename = self.save_file("Plot output files", "dat")
    # Do nothing if no .inp file has been indicated
    if not filename: return

    # Check if the .dat file name is present
    if not hasattr(self, 'active_dat_file') or not hasattr(self, 'active_plt_file'):
      # Pop-up an error message
      messagebox.showerror("Error", "Error: no plot output '.dat' file is present.")
      return

    # Copy the content of source to destination
    dest = copyfile(self.active_dat_file, filename)
    plt_filedir = os.path.dirname(dest)
    dest_name = os.path.basename(dest).split('.')[0]
    dest_filename = os.path.join(plt_filedir, dest_name + '.plt')

    copyfile(self.active_plt_file, dest_filename)

    # Provide a message to the status bar
    self.status_bar.set_text("Saved .inp file: " + filename)

  def create_menu(self):
    """
    Method that creates and adds a menu bar to the main window. It also builds the
    menu commands for each menu category.
    TODO - create a new class that enables the presence of a tooltip for each menu item.
    """
    menubar = tk.Menu(self)
    # Create the "File" menu
    filemenu = tk.Menu(menubar, tearoff=0)
    # Create the "Load" submenu
    loadmenu = tk.Menu(filemenu, tearoff=0)
    # Create the "Save" submenu
    savemenu = tk.Menu(filemenu, tearoff=0)

    # Add the "File" menu commands
    # FIXME "New" command is disabled until a better knowledge on new windows
    filemenu.add_command(label="New", accelerator="Ctrl+N", command=self.reset_main_window)
    filemenu.add_command(label="Open", accelerator="Ctrl+O", command=self.open_pli_file)

    # Append the "Load" submenu to the "File" menu
    filemenu.add_cascade(menu=loadmenu, label="Load")
    # Append the "Save" submenu to the "File" menu
    # FIXME uncomment the 'Save' menu when functionalities will be ready
    # filemenu.add_cascade(menu=savemenu, label="Save")

    filemenu.add_command(label="Set output folder", accelerator="Ctrl+W", command=self.select_output_folder)
    # Add a separator
    filemenu.add_separator()
    filemenu.add_command(label="Quit", accelerator="Ctrl+Q", command=self.quit)

    # Add the "Load" submenu commands
    loadmenu.add_command(label=".inp file", command=self.load_inp_file)
    loadmenu.add_command(label=".dat/.plt files", command=self.load_output_files)
    # Add the "Save" submenu commands
    # FIXME uncomment the 'Save' submenus when functionalities will be ready
    # savemenu.add_command(label=".inp file", command=self.save_inp_file)
    # savemenu.add_command(label=".dat/.plt files", command=self.save_output_files)

    # Append the "File" menu to the menubar
    menubar.add_cascade(menu=filemenu, label="File")
    # Add the menu bar to the main window
    self.configure(menu=menubar)

  def quit_app(self, event=None):
    """
    Method that quit the application.
    """
    # Destroy the main window and all its widgets, thus closing the application
    self.destroy()

  def reset_main_window(self, event=None):
    """
    Method that resets the main window by clearing the content of the entry widget for
    setting the path to the input .pli file, as well as the message provided by the
    status bar. It also re-builds all the 'TuPlot' and 'TuStat' tabs thus allowing users
    a fresh restart.
    """
    print("Resetting the main window...")
    # Delete the content of the .pli entry
    self.pli_entry.entry.delete(0, tk.END)
    # Clear the content of the status bar
    self.status_bar.set_text("")
    # Re-build the plot tabs
    self.build_tabs_area()


def new_postprocessing(event=None):
  """
  Function that opens a new window for performing post-processing of results from a TU simulation.
  """
  # Instantiate the TuPostProcessingGui class by passing the window title and its dimensions
  window = TuPostProcessingGui("TU Post-Processing Interface", 1377, 679)
  # Start the window loop event
  window.mainloop()

if __name__ == "__main__":
  # Call the function for running the application
  try:
    new_postprocessing()
  except Exception as e:
    print(e)
    # If any exception is caught, exit
    exit()