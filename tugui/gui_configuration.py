from enum import Enum
import os
import platform
import re

from dataclasses import dataclass

class IDGA(Enum):
  """
  Enumeration storing the different types of plots (field "Type").
  """
  IDGA_1: str = "1 - Different Curve Numbers"
  IDGA_2: str = "2 - Different Times"
  IDGA_3: str = "3 - Different Slices"

class IANT(Enum):
  """
  Enumeration storing the different types of IANT field.
  """
  IANT_1: str = "IANT 1"
  IANT_2: str = "IANT 2"
  IANT_3: str = "IANT 3"

@dataclass
class Diagram():
  """
  Dataclass providing a record storing the basic features of a diagram.
  """
  number: str = '000'

@dataclass
class TuPlotDiagram(Diagram):
  """
  Dataclass providing a record storing the features of a TuPlot diagram.
  """
  group: str = 'Radius'
  idga: str = '1'

  def define_group_from_num(self) -> None:
    """
    Method that evaluates the group value based on the diagram number and
    set the corresponding class attribute.
    """
    if int(self.number) >= 101 and int(self.number) <= 140:
      self.group = 'Radius'
    elif int(self.number) >= 201 and int(self.number) <= 251:
      self.group = 'Time'
    elif int(self.number) >= 252 and int(self.number) <= 270:
      self.group = 'Time Integral'
    elif int(self.number) >= 301 and int(self.number) <= 340:
      self.group = 'Axial'

@dataclass
class TuStatDiagram(Diagram):
  """
  Dataclass providing a record storing the features of a TuPlot diagram.
  """
  group: str = ''


class GuiPlotFieldsConfigurator():
  """
  Class that reads the configuration files and extract the values in order to build
  the option fields into the GUI. These configuration files are:
  . Diagrams - file storing the plot numbers for each plot "Group"
  . Group 1/2/2a/3 - file storing the available Kns for each plot "Number"
  . Statdiag - file storing the plot numbers related to a statistical simulation.
  A dictionary is built storing the plot "Group" VS a dictionary of the corresponding
  "Number" VS their Kns.
  As for the statistical diagrams, a dictionary of number VS their descriptive string is
  built as well.
  These configuration files need to be present in the "config" folder of the application.
  Their presence is checked before extracting the plots information.
  """
  def __init__(self):
    # Build the paths to the configuration files
    self.diagr_path: str = os.path.join(os.getcwd(), "../resources/config" + os.sep + "Diagrams")
    self.g1_path: str = os.path.join(os.getcwd(), "../resources/config" + os.sep + "Group1")
    self.g2_path: str = os.path.join(os.getcwd(), "../resources/config" + os.sep + "Group2")
    self.g2a_path: str = os.path.join(os.getcwd(), "../resources/config" + os.sep + "Group2a")
    self.g3_path: str = os.path.join(os.getcwd(), "../resources/config" + os.sep + "Group3")
    self.stat_path: str = os.path.join(os.getcwd(), "../resources/config" + os.sep + "Statdiag")

    # Check the configuration files existence into the application "config" folder
    self.check_config_file_existence(self.diagr_path, "Diagrams")
    self.check_config_file_existence(self.g1_path, "Group1")
    self.check_config_file_existence(self.g2_path, "Group2")
    self.check_config_file_existence(self.g2a_path, "Group2a")
    self.check_config_file_existence(self.g3_path, "Group3")
    self.check_config_file_existence(self.g3_path, "Statdiag")

    print("###\nConfiguration files are present in the \"resources/config\" folder\n###")

    ######################################################
    # Extract the information from the configuration files
    ######################################################
    # Open the different "Group" files and fill the dictionary "Number"-"Kn"
    numberVsKn = dict()
    self.build_nVsKn(self.g1_path, numberVsKn, "^1\d\d")
    self.build_nVsKn(self.g2_path, numberVsKn, "^2\d\d")
    self.build_nVsKn(self.g2a_path, numberVsKn, "^2\d\d")
    self.build_nVsKn(self.g3_path, numberVsKn, "^3\d\d")

    # Instantiate the dictionary holding the plots "Group" Vs the dictionary of corresponding "Number"-s VS "Kn"-s
    self.groupVSnumVsKn: dict = dict()
    # Initialize a string holding the "Group" name
    group_name = ""

    # Open the "Diagram" file and extract each of the plot "Number"-s for each "Group"
    # Open the given "Group" file by specifying the ANSI encoding they are built with
    with open(self.diagr_path, 'r', encoding="cp1252") as dg:
      # Process the file line by line
      for line in dg:
        # Get the line specifying the plot "Group"
        if re.search("^Group\s+\d.*", line.split('\n')[0]):
          # Check if the saved "Group" name differs from the current line
          if(group_name != "" and group_name != line.split(" : ")[1]):
            # Assemble the entry of the dictionary of "Group" VS dictionary of "Number" VS "Kn"-s
            self.groupVSnumVsKn[group_name] = numVskn

          # Declare a dictionary holding the plot "Number" VS the corresponding "Kn"-s of the current "Group"
          numVskn = dict()
          # Save the "Group" name
          group_name = line.split(' : ')[1].split('\n')[0]
          # Continue with the next line
          continue
        elif re.search("^\d\d\d\s+.*", line.split('\n')[0]):
          # Get the "Number" from the current line
          num = line.split(' ')[0]
          # Search for the number in the "Number" VS "Kn"-s dictionary
          if num in numberVsKn:
            numVskn[line.split('\n')[0]] = numberVsKn[num]

      # Add the last entry of the dictionary of "Group" VS dictionary of "Number" VS "Kn"-s
      self.groupVSnumVsKn[group_name] = numVskn

      # Build a dictionary of plot "Group" VS the available "Type" values
      self.groupVStype: dict = {
        list(self.groupVSnumVsKn.keys())[0]: ["1 - Different Curve Numbers", "2 - Different Times", "3 - Different Slices"],
        list(self.groupVSnumVsKn.keys())[1]: ["1 - Different Curve Numbers", "3 - Different Slices"],
        list(self.groupVSnumVsKn.keys())[2]: ["1 - Different Curve Numbers"],
        list(self.groupVSnumVsKn.keys())[3]: ["1 - Different Curve Numbers", "2 - Different Times"]
      }

    # Build a tuple storing the available options for specific plot "Number"-s
    self.iant1: tuple = ([113], ["Temperature-distribution will be drawn over the fuel, the cladding and the structure"])
    self.iant2: tuple = ([102, 103, 104, 105, 106, 107, 108],
                         ["The radial stresses and strains are only drawn for the cladding",
                         "The radial stresses and strains are only drawn for the fuel"])

    # Build a map between the IDGA enumeration and their index
    self.idgaVSi: dict = {
      IDGA(IDGA['IDGA_1']).value: 1,
      IDGA(IDGA['IDGA_2']).value: 2,
      IDGA(IDGA['IDGA_3']).value: 3,
    }

    print(self.idgaVSi)


    # Build an enumeration holding the available values of the IANT1 option, only available
    # if the selected "Number" is 113
    # self.iant1 = Enum('IANT1', ['Y', 'N'])
    # p = self.iant1.N.name
    # print("##\n", p)

    # Build the dictionary of plot number VS their descriptive string for the statistical case
    self.sta_numVSdescription: dict = dict()
    with open(self.stat_path, 'r', encoding="cp1252") as st:
      # Process the file line by line
      for line in st:
        # Get the line specifying the plot number avoiding those lines indicating as
        # "Dummy-Diagram"
        if re.search("^\d+\s+(?!.*Dummy-Diagram).*", line.split('\n')[0]):
          # Extract the plot number as an integer
          num = int(line.split(' ')[0])
          # Add the number VS descriptive line into the statistical plot dictionary
          self.sta_numVSdescription[num] = line.strip()

    #############################################################################
    # Check the presence of the TuPlot and TuStat executables in the "bin" folder
    #############################################################################
    # Check the executables existence in the "bin" folder on the basis of the
    # current OS
    if platform.system() == "Linux":
      print("LINUX HERE!")
      self.tuplot_path: str = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "tuplotgui_nc")
      self.tustat_path: str = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "tustatgui_nc")
      self.check_exe_file_existence(self.tuplot_path, "tuplotgui_nc")
      self.check_exe_file_existence(self.tustat_path, "tustatgui_nc")
    elif platform.system() == "Windows":
      print("WINDOWS HERE!")
      self.tuplot_path: str = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "TuPlotGUI.exe")
      self.tustat_path: str = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "TuStatGUI.exe")
      self.check_exe_file_existence(self.tuplot_path, "TuPlotGUI.exe")
      self.check_exe_file_existence(self.tustat_path, "TuStatGUI.exe")

    print("###\nExecutables files are present in the \"../resources/exec\" folder\n###")

  def build_nVsKn(self, group_file: str, group_dict: dict, search_num: str) -> None:
    """
    Method that, given the "Group" file to read (its path), it fills the input dictionary with:
    . keys, being the line indicating the plot "Number"
    . values, being a list of lines indicating the available Kn-s for the corresponding plot "Number"
    """
    # Open the given "Group" file by specifying the ANSI encoding they are built with
    with open(group_file, 'r', encoding="cp1252") as g1:
      # Process the file line by line
      for line in g1:
        # Get the line specifying the plot "Number"
        num = re.search(search_num, line.split('\n')[0])
        if num:
          # Declare a list holding the Kn-s of the current found "Number"
          kns = list()
          # Get the lines specifying the Kn-s corresponding to the current found "Number"
          while True:
            # Read the following line
            line = g1.readline()
            # Check for the presence of an empy line indicating the end of the Kn-s for the
            # current "Number"
            if (line.isspace() or line == "end\n"):
              # Add the "Number"-Kn entry of the dictionary
              group_dict[num.group(0)] = kns
              break
            else:
              # Add the Kn line to a list belonging to the current found "Number"
              kns.append(line.strip())


  def check_config_file_existence(self, path2check: str, filename: str) -> None:
    """
    Method that raises an exception if the given path does not correspond to an
    existing file.
    """
    if (not os.path.isfile(path2check)):
      # Raise an exception
      raise FileNotFoundError("Error: missing \"" + filename + "\" configuration file")

  def check_exe_file_existence(self, path2check: str, filename: str) -> None:
    """
    Method that raises an exception if the given path does not correspond to an
    existing executable file with right permission.
    """
    self.check_config_file_existence(path2check, filename)
    # Check that the file has execution permission
    if (not os.access(path2check, os.X_OK)):
      # Raise an exception
      raise PermissionError("Error: the \"" + filename + "\" does not have execution permission")


if __name__ == "__main__":
  # Instantiate the class
  gui_config = GuiPlotFieldsConfigurator()
  # Print the built dictionaries
  print(gui_config.groupVSnumVsKn)
  print(gui_config.sta_numVSdescription)
