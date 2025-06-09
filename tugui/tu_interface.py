import os
import platform
import shutil
from typing import Dict, List, Tuple
from typing_extensions import Self
import numpy as np
from numpy.typing import NDArray
import re

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from gui_configuration import DiagramCharacteristics
from io import TextIOWrapper


@dataclass
class TuInp:
  """
  Dataclass that records all the needed fields describing the configuration
  for a diagram as specified in an .inp plot configuration file.
  """
  file_name: str = ""
  plot_index: int = 1
  is_tuplot: bool = True
  iplot: str = '1'
  pli_name: str = ""
  idnf: str = ""
  diagram_config: str = ""
  ikon: str = ""

  diagr_type: DiagramCharacteristics = None

  @staticmethod
  def configure_tuplot_inp_fields(info: Dict[str, str]) -> Self:
    """
    Method that builds and configures the fields of the 'TuInp' dataclass
    for the 'TuPlot' case. This is done by getting the needed information
    from the input dictionary that holds the plot configuration of a single
    diagram.
    """
    # Instantiate the 'TuInp' dataclass
    tuinp = TuInp()
    # Set the default file name for the 'TuPlot' case
    tuinp.file_name = "TuPlot.inp"
    # Set the .pli file name
    tuinp.pli_name = info['PLI']
    # Set the plot number (IDNF)
    tuinp.idnf = info['IDNF']
    # Set the type of diagram
    tuinp.diagr_type = DiagramCharacteristics.init_tuplot_DiagramCharacteristics(
      number=tuinp.idnf, idga=info['IDGA'])
    # Set the keyword stating the end of the plot/diagram/file
    tuinp.ikon = info['IKON']

    # --------------------------------------------------
    # Store the diagram configuration as a single string
    # --------------------------------------------------
    # Store the IDNF value (diagram number), followed by the IDGA value (diagram type),
    # followed by NKN (nuber of curves to plot)
    tuinp.diagram_config += info['IDNF'] + " " + info['IDGA'] + " " + info['NKN'] + "\n"
    # Store on the same line:
    # . IANT1 value (Y, N), valid for plot 113, indicates the temperature distribution is considered
    # . IANT2 value (C, F), valid for plots 102-108, indicates the stresses are considered for cladding (C) or fuel (F)
    # . IANT3 value (Y, N), driver for printing the input data and X-Y table (Y) or nothing (N)
    tuinp.diagram_config += info['IANT1'] + " " + info['IANT2'] + " " + info['IANT3'] + "\n"
    # Store the curves number in increasing order:
    # . IDGA = 1, it is a list of the selected curves Kn-s
    # . IDGA = 2/3, it is equal to 1
    tuinp.diagram_config += info['KN'] + "\n"
    # Store the curves slices in increasing order:
    # . IDGA = 1/2, it is equal to 1
    # . IDGA = 3, it is a list of the selected curves slices
    tuinp.diagram_config += info['NLSUCH'] + "\n"
    # Store the time instants at which the curves are plotted or the start/end values (depending on plot group)
    tuinp.diagram_config += info["TIME"] + "\n"
    # Store the NMAS value, stating if a custom scaling is present (value fixed at 0, i.e. no custom extrema)
    tuinp.diagram_config += info["NMAS"] + "\n"

    # Return the built dataclass instance
    return tuinp

  @staticmethod
  def configure_tustat_inp_fields(info: Dict[str, str]) -> Self:
    """
    Method that builds and configures the fields of the 'TuInp' dataclass
    for the 'TuStat' case. This is done by getting the needed information
    from the input dictionary that holds the plot configuration of a single
    diagram.
    """
    # Instantiate the 'TuInp' dataclass
    tuinp = TuInp()
    # Set the default file name for the 'TuStat' case
    tuinp.file_name = "TuStat.inp"
    # Set the .pli file name
    tuinp.pli_name = info['PLI']
    # Set the plot number (DIAGNR)
    tuinp.idnf = info['DIAGNR']
    # Set the type of diagram
    tuinp.diagr_type = DiagramCharacteristics(number=tuinp.idnf)
    # Set the flag stating the diagram is not a 'TuPlot' case
    tuinp.is_tuplot = False
    # Set the keyword stating the end of the plot/diagram/file
    tuinp.ikon = info['CONTIN']

    # --------------------------------------------------
    # Store the diagram configuration as a single string
    # --------------------------------------------------
    # Store the DIAGNR value (diagram number)
    tuinp.diagram_config += info['DIAGNR'] + "\n"
    # Store the number of required section/slice
    tuinp.diagram_config += info['NAXIAL'] + "\n"
    # Store the time instants at which the curves are plotted
    tuinp.diagram_config += info["TIME"] + "\n"
    # Store the number of intervals of the statistical distribution (INTERV)
    tuinp.diagram_config += info["INTERV"] + "\n"
    # Store the type of distribution (DISTR)
    tuinp.diagram_config += info["DISTR"] + "\n"

    # Return the built dataclass instance
    return tuinp


class InpHandler():
  """
  Class for handling the functionalities devoted to reading and writing a plot
  configuration .inp file.
  """
  def __init__(self, inp_path: str) -> None:
    """
    Construct an instance of this class by receiving the path to the .inp file.
    """
    # Store the paths to the .inp file (to read or write) and its directory
    self.inp_path = inp_path
    self.inp_dir = os.path.dirname(self.inp_path)

  def read_inp_file(self) -> None:
    """
    Method that reads an input .inp file and interprets its content according to
    the specific 'TuPlot' or 'TuStat' subroutine it was created from.
    """
    # Declare a list of dataclasses holding the configuration values for
    # each diagram declared in the loaded input file
    self.diagrams_list: List[TuInp] = list()
    # Declare an index representing the plot index number
    plot_index = 0

    # Open the file for reading
    with open(self.inp_path, 'r') as inp:
      # Read each line
      for line in inp:
        # Strip any whitespace
        line = line.strip()
        # Skip any existing comment line starting with a '+'
        if line.startswith('+'):
          continue

        # Get the beginning of a plot description
        if "IDEN" in line:
          # Update the plot index number
          plot_index += 1
          # Extract and store all the information describing the plot configuration of a single diagram
          self._extract_diagram_info(plot_index, inp)

  def save_inp_file(self, diagrams: List[TuInp]) -> None:
    """
    Method that saves 1 or more plot configuration diagrams on a single .inp file.
    The plots configuration are provided as a list of 'TuInp' dataclasses storing
    all the needed information to be written on file.
    """
    # Save the .inp file containing the plots configuration options
    with open(self.inp_path, 'w') as f:
      # Loop over all the dataclasses of the list
      for diagr in diagrams:
        # Write the lines of the file
        f.write('IDEN\n')
        f.write(diagr.iplot + '\n')
        f.write(diagr.pli_name + '\n')
        f.write(diagr.diagram_config)
        f.write(diagr.ikon + '\n')

  def save_loaded_inp(self) -> str:
    """
    Method that saves the loaded .inp file in the current working directory
    if its name is different from 'TuPlot.inp' or 'TuStat.inp', as the post-
    processing TU executables requires these specific file names.
    """
    # Check if all stored diagrams configurations refers to the same kind of diagrams,
    # i.e. all TuPlot or TuStat ones. If not the case, raise an exception.
    if not all(diagr.is_tuplot == self.diagrams_list[0].is_tuplot for diagr in self.diagrams_list):
      raise Exception("ERROR: The loaded .inp file contains mixed-type diagrams.")
    # Check if any of the .pli files mentioned in the .inp file is missing
    for diagr in self.diagrams_list:
      # Instantiate the class that extracts the .pli file content. It also checks
      # the file existence and retrieve the DAT file names whose presence needs
      # to be checked as well.
      if os.path.dirname(diagr.pli_name):
        plireader = PliReader.init_PliReader(diagr.pli_name)
      else:
        plireader = PliReader.init_PliReader(os.path.join(self.inp_dir, diagr.pli_name))
      # Check if any of the DAT files is missing
      check_file_existence(os.path.join(self.inp_dir, plireader.mac_path), 'mac')
      check_file_existence(os.path.join(self.inp_dir, plireader.mic_path), 'mic')
      # Check the .sta file existence only if required, i.e if the 'ISTATI' field is '1'
      if plireader.opt_dict['ISTATI'] == 1:
        check_file_existence(os.path.join(self.inp_dir, plireader.sta_path), 'sta')

    # Declare a string holding the .inp filename (with default to 'TuPlot')
    filename = "TuPlot.inp"
    # Get the name of the loaded .inp file
    inp_name = os.path.basename(self.inp_path).split(os.sep)[-1]
    # Re-declare the file name if 'TuStat' case
    if not self.diagrams_list[0].is_tuplot:
      filename = "TuStat.inp"

    # Return if the loaded .inp file name does not differ from the default one
    if inp_name == filename: return os.path.join(self.inp_dir, filename)

    # Change the .inp file path instance variable to reflect the standard file name required
    # by the plotting executables
    self.inp_path = os.path.join(self.inp_dir, filename)

    # Save the .inp file containing the plots configuration options in the output folder
    self.save_inp_file(self.diagrams_list)

    # Return the path to the saved .inp file
    return os.path.join(self.inp_dir, filename)

  def _extract_diagram_info(self, plot_index: int,
                            inp_file_handle: TextIOWrapper) -> None:
    """
    Method that extract from the given 'TextIOWrapper' instance, given by opening the
    .inp file for reading, all the information about the plot configuration of a single
    diagram. These are used to set the fields of an instance of the 'TuInp' dataclass
    which is added to the instance variable list storing all the present diagrams.
    """
    # Declare a new dataclass recording the plot configuration fields
    inp_config = TuInp()
    # Store the basic information
    inp_config.file_name = self.inp_path
    inp_config.plot_index = plot_index

    # Read the IPLOT field line and store it
    inp_config.iplot = inp_file_handle.readline().strip()
    # Read the .pli name field line and store it
    inp_config.pli_name = inp_file_handle.readline().strip()

    # Read the line containing the 'IDNF' value in order to interpret the plot:
    # . if this line contains 3 values, the .inp file corresponds to a 'TuPlot' case
    # . if this line contains 1 value only, the .inp file corresponds to a TuStat case
    inp_config.diagram_config += inp_file_handle.readline()
    if len(inp_config.diagram_config.split()) == 1:
      # Only one value --> 'TuStat' case
      inp_config.is_tuplot = False
      # Declare the dataclass for the 'TuStat' case
      inp_config.diagr_type = DiagramCharacteristics(number=inp_config.diagram_config.split()[0])
    else:
      # Declare the dataclass for the 'TuPlot' case and evaluate its group according to
      # the given plot number
      inp_config.diagr_type = DiagramCharacteristics.init_tuplot_DiagramCharacteristics(
        number=inp_config.diagram_config.split()[0],
        idga=inp_config.diagram_config.split()[1])

    # Get the plot number
    inp_config.idnf = inp_config.diagram_config.split()[0]

    # Loop over all the lines until the diagram end tag is reached
    for line in inp_file_handle:
      # Exit the loop if the diagram section has ended
      if line.startswith('+') or any(substring in line for substring in ['D', 'I', 'E']):
        print("##### DIAGRAM END #####")
        # Store the 'IKON' field value
        inp_config.ikon = line.strip()
        # Add the built dataclass to the list of diagrams
        self.diagrams_list.append(inp_config)
        # Return since diagram reading has finished
        return

      # Store the diagram configuration
      inp_config.diagram_config += line


def check_file_existence(file_path: str, file_extension: str) -> None:
  """
  Function that can be accessed globally for checking if the given
  file path exists and is a file. If not, the function raises an
  exception.
  """
  if not os.path.isfile(file_path):
    # If the file does not exists, throw an exception
    raise Exception(f"Error: the .{file_extension} file does not exist at the specified path.")


@dataclass
class DatGenerator():
  """
  Class that stores information about the paths of the input and output
  files and that are needed for running the plotting executable.
  """
  plotexec_path: str = ''
  inp_path: str = ''
  inp_dir: str = ''
  output_path: str = ''
  dat_paths: List[str] = field(default_factory=list)
  plt_paths: List[str] = field(default_factory=list)
  out_paths: List[str] = field(default_factory=list)

  @staticmethod
  def init_DatGenerator_and_run_exec(plotexec_path: str, inp_path: str,
                                     plots_num: int, cwd: str,
                                     output_files_name: str) -> Self:
    """
    Static method that initialize the 'DatGenerator' dataclass by providing all the needed
    information received as input to this function.
    Some checks are performed beforehands, that is on the existence of the .inp file
    at the specified path and of the output directory.
    Given the specific OS, the paths of the output .dat, .plt and .out files are built
    accordingly.
    Afterwards, a function is called to run the plotting executable which produces the
    output files in the specified working directory, while updating the paths to the output
    .dat and .plt files.

    Hence, this method returns an object of the 'DatGenerator' dataclass.
    """
    # Check the input .inp file existence; raise an Exception if not found
    if not os.path.isfile(inp_path):
      # The file does not exist, hence raise an exception
      raise Exception("Error: the .inp file does not exist at the specified path.")
    # Get the path to the .inp file directory
    inp_dir = os.path.dirname(inp_path)

    # Check the output directory existence; raise an Exception if not found
    if not os.path.isdir(cwd):
      # The output directory does not exist, hence raise an exception
      raise Exception(f"Error: the output '{cwd}' folder does not exist at the specified path.")

    # Given the number of diagrams to produce, build a list of output file names
    dat_paths = list()
    plt_paths = list()
    out_paths = list()

    # Build the paths to the output files that will be written by running the executable
    for i in range(plots_num):
      if platform.system() == "Linux":
        dat_paths.append(os.path.join(inp_dir, output_files_name + str(i + 1).zfill(2) + ".dat"))
        plt_paths.append(os.path.join(inp_dir, output_files_name + str(i + 1).zfill(2) + ".plt"))
        out_paths.append(os.path.join(inp_dir, output_files_name + ".out"))
      elif platform.system() == "Windows":
        dat_paths.append(os.path.join(inp_dir, output_files_name + ".dat"))
        plt_paths.append(os.path.join(inp_dir, output_files_name + ".plt"))
        out_paths.append(os.path.join(inp_dir, output_files_name + ".out"))

      print("DIR --> " + inp_dir)
      print("DAT --> " + dat_paths[i])
      print("PLT --> " + plt_paths[i])
      print("OUT --> " + out_paths[i])

    # Buil an object of the 'DatGenerator' class with the given data
    dat_gen = DatGenerator(
      plotexec_path=plotexec_path,
      inp_path=inp_path,
      inp_dir=inp_dir,
      output_path=cwd,
      dat_paths=dat_paths,
      plt_paths=plt_paths,
      out_paths=out_paths
    )

    # Call the function that runs the plotting executables, given the information
    # stored within the 'DatGenerator' dataclass
    run_plot_files_generation(dat_gen)

    # Return an object of the 'DatGenerator' class, built with the given data
    return dat_gen


def run_plot_files_generation(datGen: DatGenerator) -> Self:
  """
  Function that runs the plotting executable by feeding it with the .inp file.
  Since the run needs to be in the folder of the .inp input file, the current
  working directory is moved to the one of this file.
  Afterwards, the plotting executable is run and the output .dat, .plt and .out
  files are moved into the specified output directory, stored in the given
  object of the 'DatGenerator' dataclass. If any of the .dat and .plt files has
  not been created (a specific check is run), an exception is risen.
  If the creation succedes, the corresponding paths stored in the given
  'DatGenerator' dataclass object are updated.

  The function hence returns the updated dataclass.
  """
  # The current working directory is changed to the one of the .inp file
  os.chdir(os.path.dirname(datGen.inp_path))
  print("CURRENT WD: " + os.getcwd())

  # Assemble the command for running the executable
  command = datGen.plotexec_path + " " + os.path.basename(datGen.inp_path).split(os.sep)[-1]
  # Run the tuplotgui executable by passing the input file
  print("RUN: " + command)
  os.system(command)

  # Check for the presence of all of the output files
  for i in range(len(datGen.dat_paths)):
    if (os.path.isfile(datGen.dat_paths[i]) and os.path.isfile(datGen.plt_paths[i])):
      # Move the output files into the user-specified working directory
      shutil.move(datGen.dat_paths[i], os.path.join(datGen.output_path, os.path.basename(datGen.dat_paths[i]).split(os.sep)[-1]))
      shutil.move(datGen.plt_paths[i], os.path.join(datGen.output_path, os.path.basename(datGen.plt_paths[i]).split(os.sep)[-1]))

      # Change the paths of the output files to the ones where they have just been moved
      datGen.dat_paths[i] = os.path.join(datGen.output_path, os.path.basename(datGen.dat_paths[i]).split(os.sep)[-1])
      datGen.plt_paths[i] = os.path.join(datGen.output_path, os.path.basename(datGen.plt_paths[i]).split(os.sep)[-1])
    else:
      # If any of the output files does not exist, raise an exception
      raise Exception("Error: something wrong with the output extraction.\
                      One of the output files has not been produced.")
    # Handle the .out file case: given how the executables have been compiled, this file could not be present
    if os.path.isfile(datGen.out_paths[i]):
      # Move the output file into the user-specified working directory
      shutil.move(datGen.out_paths[i], os.path.join(datGen.output_path, os.path.basename(datGen.out_paths[i]).split(os.sep)[-1]))
      # Change the path of the output file to the one where it has just been moved
      datGen.out_paths[i] = os.path.join(datGen.output_path, os.path.basename(datGen.out_paths[i]).split(os.sep)[-1])
    else:
      # Set an empty string as the .out file path in case it has not been produced
      datGen.out_paths[i] = ""

    print("OUTPUT FILES: " + datGen.dat_paths[i] + ", " + datGen.plt_paths[i] + ", " + datGen.out_paths[i])

  # Restore the previous working directory
  os.chdir(datGen.output_path)

  # Return the updated dataclass
  return datGen

@dataclass
class PliReader():
  """
  Datalass that interprets the content of the .pli file produced by the TU simulation. It contains
  information useful for extracting data from the .mac e .mic files.
  """
  pli_path: str = ''
  pli_folder: str = ''
  opt_dict: Dict[str, str] = field(default_factory=dict)
  mic_path: str = ''
  mac_path: str = ''
  sta_path: str = ''
  mic_recordLength: str = ''
  mac_recordLength: str = ''
  sta_recordLength: str = ''
  sta_micStep: str = ''
  sta_macStep: str = ''
  sta_dataset: str = ''
  axial_steps: str = ''

  @staticmethod
  def init_PliReader(pli_path: str) -> Self:
    """
    Method that builds and configures the 'PliReader' dataclass by providing all
    the needed information that come by interpreting the content of the .pli file
    produced by the TU simulation.
    It receives as parameter the path to the .pli file to read and checks the actual
    existence of the file. If no exception are risen, the fields of the 'PliReader'
    dataclass are set.
    This method returns the built instance of the 'PliReader' class.
    """
    # Check the .pli file existence
    check_file_existence(pli_path, 'pli')
    # Get the path to the .pli file directory
    pli_dir = os.path.dirname(pli_path)
    # Instantiate the 'PliReader' class
    pli_reader = PliReader(pli_path=pli_path, pli_folder=pli_dir)

    # Open the .pli file in reading mode
    with open(pli_path, 'r') as f:
      # Read line-by-line
      for line in f:
        # Get the line where the options are printed
        if (("M3" in line) and ("ISTRUK" in line)):
          # Split the line to get the list of option names
          options = line.split()
          # Advance to the next line and get the list of the option values
          options_values = f.readline().split()
          # Check if the two lists have the same size
          if (len(options) != len(options_values)):
            # Raise an exception
            raise Exception("Error: no match between the options and their values")

          # Build a dictionary holding the name of the options VS their values
          pli_reader.opt_dict = {options[i]: options_values[i] for i in range(len(options))}
        else:
          # Pattern specifying any letter, digit, underscore or hyphen to find
          # in lines
          pattern = "[a-zA-Z0-9_-]+"
          # Search for the lines where the paths of the .mic and .mac files and their record length are present
          if (re.search("^" + pattern + "\.mic\s+", line)):
            # Save the path to the .mic file
            pli_reader.mic_path = line.split()[0]
            # Advance to the next line to get the .mic record length
            pli_reader.mic_recordLength = f.readline().split()[0]
          elif(re.search("^" + pattern + "\.mac\s+", line)):
            # Save the path to the .mac file
            pli_reader.mac_path = line.split()[0]
            # Advance to the next line to get the .mac record length
            pli_reader.mac_recordLength = f.readline().split()[0]
          elif(re.search("^" + pattern + "\.sta\s+", line)):
            # Save the path to the .sta file
            pli_reader.sta_path = line.split()[0]
            # Advance to the next line to get the .sta record length
            pli_reader.sta_recordLength = f.readline().split()[0]
            # Advance to the next line to get the .sta micro-step dataset record length
            pli_reader.sta_micStep = f.readline().split()[0]
            # Advance to the next line to get the .sta macro-step dataset record length
            pli_reader.sta_macStep = f.readline().split()[0]
            # Advance to the next line to get the .sta statistic dataset record length
            pli_reader.sta_dataset = f.readline().split()[0]

    # Extract the number of axial sections depending on the ISLICE field
    if pli_reader.opt_dict['ISLICE'] == 1:
      pli_reader.axial_steps = int(pli_reader.opt_dict['M3'])
    else:
      pli_reader.axial_steps = int(pli_reader.opt_dict['M3']) + 1

    # Return the built instance
    return pli_reader


class DaReader(ABC):
  """
  Base class for all the ones that interpret the content of a direct-access file produced
  by the TU simulation.
  It provides methods to be overridden by its subclasses.
  """
  def __init__(self, da_path: str, extension: str) -> None:
    """
    Build an instance of the 'DaReader' class. It receives as parameter the path to the
    direct-access file to read and checks its actual existence.
    """
    # Check the direct-access file existence
    check_file_existence(da_path, extension)
    # Store the direct-access file path
    self.da_path: str = da_path
    # Initialize the time values read from the direct-access file
    self.time_h: List[int] = list()
    self.time_s: List[int] = list()
    self.time_ms : List[int] = list()
    # Call the ABC constructor
    super().__init__()

  @abstractmethod
  def extract_time_hsms(self, record_length: int) -> Tuple[List[int], List[int], List[int]]:
    """
    Method that extracts from the direct-access file the simulation time instants
    as arrays for hours, seconds and milliseconds respectively. These arrays are
    saved as instance attributes and returned as a tuple.
    """

  @abstractmethod
  def read_tu_data(self, record_length: int) -> NDArray[np.float32]:
    """
    Method that opens the direct-access file and re-elaborate its content, originally stored
    as a one-line array. Given the record length, the array is reshaped as a 2D array having:
    . as rows, the values at each time for each igrob-slice
    . as columns, the values of the quantities calculated for each m2(igrob)-slice element
    Subclasses can override this method providing their own implementation in case the one
    proposed is not valid (case of a .sta file).
    """


class MicReader(DaReader):
  """
  Class that interprets the content of the .mic file produced by the TU simulation.
  For every micro-step (TU internal step) several quantities are stored, that are
  section/slice dependent variables and special quantities.
  """
  def __init__(self, mic_path: str) -> None:
    """
    Build an instance of the 'MicReader' class that interprets the content of the .mic
    file produced by the TU simulation.
    It receives as parameter the path to the .mic file to read and checks the actual
    existence of the file.
    """
    # Store the file extension
    self.extension = 'mic'
    # Call the superclass constructor
    super().__init__(mic_path, self.extension)

  def extract_time_hsms(self, record_length: int) -> Tuple[List[int], List[int], List[int]]:
    """
    Method that extracts from the direct-access file the simulation time instants
    as arrays for hours, seconds and milliseconds respectively. These arrays are
    saved as instance attributes and returned as a tuple.
    """
    da_data = self.read_tu_data(record_length)
    # Build the time arrays by extracting the values for hours, seconds (both as integers)
    # and milliseconds
    self.time_h = [int(h) for h in da_data[::, 0]]
    self.time_s = [int(s) for s in da_data[::, 1]]
    self.time_ms = da_data[::, 2]
    # Return the tuple of times
    return (self.time_h, self.time_s, self.time_ms)

  def read_tu_data(self, record_length: int) -> NDArray[np.float32]:
    """
    Method that opens the direct-access file and re-elaborate its content, originally stored
    as a one-line array. Given the record length, the array is reshaped as a 2D array having:
    . as rows, the values at each time for each igrob-slice
    . as columns, the values of the quantities calculated for each m2(igrob)-slice element
    Subclasses can override this method providing their own implementation in case the one
    proposed is not valid (case of a .sta file).
    """
    try:
      with open(self.da_path, 'rb') as f:
        # Read all the data as a 1D array of floating point values
        data = np.fromfile(f, dtype='float32', count=-1)
        # Reshape the data as a 2D array
        data = data.reshape(int(data.size / record_length), record_length)
        # Return the array
        return data
    except:
      error_msg = f"Error while extracting the data from the '{self.da_path}' file."
      raise Exception(error_msg)


class MacReader(MicReader):
  """
  Class that interprets the content of the .mac file produced by the TU simulation. It contains
  the radially dependent quantities at every simulation time for every (i, j)-th element of the
  domain.
  """
  def __init__(self, mac_path: str, n_slices: int) -> None:
    """
    Build an instance of the 'MacReader' class that interprets the content of the .mac
    file produced by the TU simulation.
    It receives as parameter the path to the .mac file to read and checks the actual
    existence of the file.
    """
    # Store the file extension
    self.extension: str = 'mac'
    # Call the superclass constructor
    super().__init__(mac_path)

    # Store the number of slices
    self.n_slices: int = n_slices

  def extract_xtime_hsms(self, record_length: int) -> Tuple[List[int], List[int], List[int]]:
    """
    Method that extracts from the .mac file the simulation time instants as arrays
    for hours, seconds and milliseconds respectively. These values are provided
    for each slice, hence the extracted arrays are filtered every n-slices values,
    saved as instance attributes and returned as a tuple.
    """
    # Extract all the occurrences of the times
    (h, s, ms) = self.extract_time_hsms(record_length)
    # Filter the time values every n-slices and store their values
    self.time_h = h[::self.n_slices]
    self.time_s = s[::self.n_slices]
    self.time_ms = ms[::self.n_slices]

    # Return the tuple of times
    return (self.time_h, self.time_s, self.time_ms)


class StaReader(DaReader):
  """
  Class that interprets the content of the .sta file produced by the TU simulation.
  For every time step (choosen by users) several quantities are stored.
  """
  def __init__(self, sta_path: str, ibyte: int) -> None:
    """
    Build an instance of the 'MicReader' class that interprets the content of the .mic
    file produced by the TU simulation.
    It receives as parameter the path to the .mic file to read and checks the actual
    existence of the file.
    """
    # Call the superclass constructor
    super().__init__(sta_path, 'sta')

    # Store the ibyte value
    self.ibyte: int = ibyte

  def extract_time_hsms(self, record_length: int, axial_steps: int,
                        sta_dataset_length: int) -> Tuple[List[int], List[int], List[int]]:
    """
    Method that overrides the superclass method for extracting the time steps from a generic
    direct-access file.
    This provides an implementation specific to the case of a .sta file for getting the time
    steps as arrays for hours, seconds and milliseconds respectively.
    These arrays are saved as instance attributes and returned as a tuple.
    """
    # Extract an array of all the data stored in the .sta file
    sta_data = self.read_tu_data(record_length, axial_steps, sta_dataset_length)
    # Get all the values of the time
    all_times = np.array(sta_data[:, 0, 0:3]).tolist()
    # Filter out any time duplicate
    list_of_times = list()
    for t in all_times:
      if t not in list_of_times:
        list_of_times.append(t)

    # Build the time arrays by extracting the values for hours, seconds (both as integers)
    # and milliseconds
    self.time_h = [int(h[0]) for h in list_of_times]
    self.time_s = [int(s[1]) for s in list_of_times]
    self.time_ms = [ms[2] for ms in list_of_times]
    # Return the tuple of times
    return (self.time_h, self.time_s, self.time_ms)

  def read_tu_data(self, record_length: int, axial_steps: int,
                   sta_dataset_length: int) -> NDArray[np.float32]:
    """
    Method that overrides the superclass method for extracting the content of a generic
    direct-access file.
    This provides an implementation specific to the case of a .sta file for re-elaborating
    its content, originally stored as a one-line array. Given the dimensions provided as
    input, the array is re-shaped as a 3D one.
    """
    try:
      # Open the file for reading
      with open(self.da_path, 'rb') as f:
        # Handle the case the data is stored as 4 or 8 byte values
        if self.ibyte == 4:
          sta_data1 = np.fromfile(f, dtype=np.float32, count=-1)
          sta_data = np.array(sta_data1, dtype=np.float64)
        elif self.ibyte == 8:
          sta_data = np.fromfile(f, dtype=np.float64, count=-1)
        else:
          error_msg = "The byte lenght of data in the '.sta' and '.sti' binary files \
                      needs to be 4 or 8."
          raise Exception(error_msg)

      # Determine the length of the X dimension of the reshaped array
      x_dim = int(sta_dataset_length / (axial_steps + 1))
      # Reshape the data in the .sta file as a 3D array and return it
      return np.reshape(sta_data, (x_dim, axial_steps+1, record_length))
    except:
      error_msg = "Error while extracting the data from the '.sta' file."
      raise Exception(error_msg)


if __name__ == "__main__":
  # Flag stating which class is being tested:
  #   1-DatGenerator
  #   2-MicReader
  #   3-PliReader
  #   4-MacReader
  #   5-StaReader
  #   6-InpHandler (loading .inp)
  test: int = 1

  match test:
    case 1:
      print("Testing the interface to Tuplotgui executable")

      # Get the absolute path of the current file
      abspath: str = os.path.abspath(__file__)
      # Get the file directory path
      dname: str = os.path.dirname(abspath)

      # Run the method that deals with instantiating the dataclass storing the needed
      # information for the plotting executable to be run. The corresponding executable
      # is run afterwards and the paths to the output .dat and .plt files, stored in the
      # returned object, are updated.
      inp_to_dat: DatGenerator = DatGenerator.init_DatGenerator_and_run_exec(
        plotexec_path=os.path.join(dname, "bin/tuplotgui_nc"),
        inp_path="../tests/input/TuPlot.inp",
        plots_num=1,
        cwd="../tests/output",
        output_files_name='TuPlot')
    case 2:
      print("Testing the interface to .mic file")
      # Extract the information from the .pli file and instantiate the 'PliReader' class
      plireader: PliReader = PliReader.init_PliReader("../Input/rodcd.pli")

      # Instantiate the MicReader class
      micreader: MicReader = MicReader(os.path.dirname(plireader.pli_path) + os.sep + plireader.mic_path)
      # Extract the time values
      (h, s, ms) = micreader.extract_time_hsms(int(plireader.mic_recordLength))
      print(h, s, ms)
    case 3:
      # PliReader case
      print("Testing the interface to the .pli file")
      # Extract the information from the .pli file and instantiate the 'PliReader' class
      plireader: PliReader = PliReader.init_PliReader("../Input/rodcd.pli")
      print("Path to the .pli file: " + plireader.pli_path)

      print(plireader.opt_dict)
      print(plireader.mic_path, plireader.mic_recordLength)
      print(plireader.mac_path, plireader.mac_recordLength)
      print(plireader.sta_path, plireader.sta_recordLength, plireader.sta_micStep, plireader.sta_macStep)

    case 4:
      print("Testing the interface to .mac file")
      # Extract the information from the .pli file and instantiate the 'PliReader' class
      plireader: PliReader = PliReader.init_PliReader("../Input/rodcd.pli")

      # Instantiate the MacReader class
      macreader: MacReader = MacReader(os.path.dirname(plireader.pli_path) + os.sep + plireader.mac_path,
                            int(plireader.opt_dict['M3']))
      # Extract the time values
      (h, s, ms) = macreader.extract_xtime_hsms(int(plireader.mac_recordLength))
      print(h, s, ms)

    case 5:
      print("Testing the interface to .sta file")
      # Extract the information from the .pli file and instantiate the 'PliReader' class
      plireader: PliReader = PliReader.init_PliReader("../Input/rodcd.pli")

      # Instantiate the StaReader class
      stareader: StaReader = StaReader(os.path.dirname(plireader.pli_path) + os.sep + plireader.sta_path,
                            int(plireader.opt_dict['IBYTE']))
      # stareader.read_tu_data(int(plireader.sta_recordLength), int(plireader.opt_dict['M3']), int(plireader.sta_dataset))
      # Extract the time values
      (h, s, ms) = stareader.extract_time_hsms(
        record_length=int(plireader.sta_recordLength),
        axial_steps=plireader.axial_steps,
        sta_dataset_length=int(plireader.sta_dataset))
      print(h, s, ms)

    case 6:
      print("Testing the interface to .inp file")
      # Instantiate the 'InpHandler' class
      inpreader: InpHandler = InpHandler("../Input/TuPlot_2diagrams.inp")
      # Read the loaded .inp file and extract its content
      inpreader.read_inp_file()
      # Save the content of the read .inp file into a file whose name complies with
      # what needed by the plotting executables
      inpreader.save_loaded_inp()
