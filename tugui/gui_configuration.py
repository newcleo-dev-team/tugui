from ast import List
from enum import Enum
import os
import platform
import re

from dataclasses import dataclass, field
from typing import Dict, Tuple, List

from plot_settings import GroupType
from support import IDGA


@dataclass
class DiagramCharacteristics():
  """
  Dataclass providing a record storing the characteristics of either a
  TuPlot or a TuStat diagram.
  """
  group: GroupType = None
  number: str = ''
  idga: str = ''

def define_diagram_group(diagr_char: DiagramCharacteristics):
  """
  Function that, given the instance of the 'DiagramCharacteristics' dataclass,
  evaluates the group value based on the diagram number.
  It then sets the corresponding attribute.
  """
  if int(diagr_char.number) >= 101 and int(diagr_char.number) <= 140:
    diagr_char.group = GroupType.group1
  elif int(diagr_char.number) >= 201 and int(diagr_char.number) <= 251:
    diagr_char.group = GroupType.group2
  elif int(diagr_char.number) >= 252 and int(diagr_char.number) <= 270:
    diagr_char.group = GroupType.group2A
  elif int(diagr_char.number) >= 301 and int(diagr_char.number) <= 340:
    diagr_char.group = GroupType.group3


@dataclass
class GuiPlotFieldsConfigurator():
  """
  Dataclass providing a record storing all the needed information for filling up
  the plot configuration fields into the GUI, as well as for enabling the plotting
  functionalities.
  To do so, some support dictionaries are stored as well.
  """
  diagr_path: str = ''
  g1_path: str = ''
  g2_path: str = ''
  g2a_path: str = ''
  g3_path: str = ''
  stat_path: str = ''
  groupVSnumVsKn: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)
  groupVStype: Dict[List, List[str]] = field(default_factory=dict)
  iant1: Tuple = tuple()
  iant2: Tuple = tuple()
  idgaVSi: Dict[str, int] = field(default_factory=dict)
  sta_numVSdescription: Dict[int, str] = field(default_factory=dict)
  tuplot_path: str = ''
  tustat_path: str = ''


def init_GuiPlotFieldsConfigurator_attrs() -> GuiPlotFieldsConfigurator:
  """

  """
  # Declare an instance of the 'GuiPlotFieldsConfigurator' dataclass
  gui_config = GuiPlotFieldsConfigurator()
  ####################################
  # Configure the dataclass attributes
  ####################################
  # ---------------------------------------
  # Build and check the configuration files
  # ---------------------------------------
  # Build the configuration folder path
  config =  os.path.join(os.getcwd(), "../resources/config")
  # Build the paths to the configuration files
  gui_config.diagr_path = os.path.join(config, "Diagrams")
  gui_config.g1_path = os.path.join(config, "Group1")
  gui_config.g2_path = os.path.join(config, "Group2")
  gui_config.g2a_path = os.path.join(config, "Group2a")
  gui_config.g3_path = os.path.join(config, "Group3")
  gui_config.stat_path = os.path.join(config, "Statdiag")

  # Check the configuration files existence into the application "config" folder
  check_config_file_existence(gui_config.diagr_path, "Diagrams")
  check_config_file_existence(gui_config.g1_path, "Group1")
  check_config_file_existence(gui_config.g2_path, "Group2")
  check_config_file_existence(gui_config.g2a_path, "Group2a")
  check_config_file_existence(gui_config.g3_path, "Group3")
  check_config_file_existence(gui_config.g3_path, "Statdiag")

  print("###\nConfiguration files are present in the \"resources/config\" folder\n###")

  # ----------------------------------------------------
  # Extract the information from the configuration files
  # ----------------------------------------------------
  # Open the different 'Group' files and fill the dictionary 'Number'-'Kn'
  numberVsKn = dict()
  _build_nVsKn(gui_config.g1_path, numberVsKn, "^1\d\d")
  _build_nVsKn(gui_config.g2_path, numberVsKn, "^2\d\d")
  _build_nVsKn(gui_config.g2a_path, numberVsKn, "^2\d\d")
  _build_nVsKn(gui_config.g3_path, numberVsKn, "^3\d\d")

  # Instantiate the dictionary holding the plots "Group" Vs the dictionary of corresponding "Number"-s VS "Kn"-s
  gui_config.groupVSnumVsKn = dict()
  # Initialize a string holding the "Group" name
  group_name = ""

  # Open the "Diagram" file and extract each of the plot "Number"-s for each "Group"
  # Open the given "Group" file by specifying the ANSI encoding they are built with
  with open(gui_config.diagr_path, 'r', encoding="cp1252") as dg:
    # Process the file line by line
    for line in dg:
      # Get the line specifying the plot "Group"
      if re.search("^Group\s+\d.*", line.split('\n')[0]):
        # Check if the saved "Group" name differs from the current line
        if(group_name != "" and group_name != line.split(" : ")[1]):
          # Assemble the entry of the dictionary of "Group" VS dictionary of "Number" VS "Kn"-s
          gui_config.groupVSnumVsKn[group_name] = numVskn

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
    gui_config.groupVSnumVsKn[group_name] = numVskn

    # Build a dictionary of plot "Group" VS the available "Type" values
    gui_config.groupVStype = {
      list(gui_config.groupVSnumVsKn.keys())[0]: ["1 - Different Curve Numbers", "2 - Different Times", "3 - Different Slices"],
      list(gui_config.groupVSnumVsKn.keys())[1]: ["1 - Different Curve Numbers", "3 - Different Slices"],
      list(gui_config.groupVSnumVsKn.keys())[2]: ["1 - Different Curve Numbers"],
      list(gui_config.groupVSnumVsKn.keys())[3]: ["1 - Different Curve Numbers", "2 - Different Times"]
    }

    # Build a tuple storing the available options for specific plot "Number"-s
    gui_config.iant1 = ([113], ["Temperature-distribution will be drawn over the fuel, the cladding and the structure"])
    gui_config.iant2 = ([102, 103, 104, 105, 106, 107, 108],
                  ["The radial stresses and strains are only drawn for the cladding",
                   "The radial stresses and strains are only drawn for the fuel"])

    # Build a map between the IDGA enumeration and their index
    gui_config.idgaVSi = {
      IDGA.IDGA_1.description: IDGA.IDGA_1.index,
      IDGA.IDGA_2.description: IDGA.IDGA_2.index,
      IDGA.IDGA_3.description: IDGA.IDGA_3.index
    }

    print(gui_config.idgaVSi)

    # Build the dictionary of plot number VS their descriptive string for the statistical case
    gui_config.sta_numVSdescription = dict()
    with open(gui_config.stat_path, 'r', encoding="cp1252") as st:
      # Process the file line by line
      for line in st:
        # Get the line specifying the plot number avoiding those lines indicating as
        # "Dummy-Diagram"
        if re.search("^\d+\s+(?!.*Dummy-Diagram).*", line.split('\n')[0]):
          # Extract the plot number as an integer
          num = int(line.split(' ')[0])
          # Add the number VS descriptive line into the statistical plot dictionary
          gui_config.sta_numVSdescription[num] = line.strip()

    # ---------------------------------------------------------------------------
    # Check the presence of the TuPlot and TuStat executables in the "bin" folder
    # ---------------------------------------------------------------------------
    # Check the executables existence in the "bin" folder on the basis of the
    # current OS
    if platform.system() == "Linux":
      print("LINUX HERE!")
      gui_config.tuplot_path = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "tuplotgui")
      gui_config.tustat_path = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "tustatgui")
      check_exe_file_existence(gui_config.tuplot_path, "tuplotgui")
      check_exe_file_existence(gui_config.tustat_path, "tustatgui")
    elif platform.system() == "Windows":
      print("WINDOWS HERE!")
      gui_config.tuplot_path = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "TuPlotGUI.exe")
      gui_config.tustat_path = os.path.join(os.getcwd(), "../resources/exec" + os.sep + "TuStatGUI.exe")
      check_exe_file_existence(gui_config.tuplot_path, "TuPlotGUI.exe")
      check_exe_file_existence(gui_config.tustat_path, "TuStatGUI.exe")

    print("###\nExecutables files are present in the \"../resources/exec\" folder\n###")

  # Return the configured 'GuiPlotFieldsConfigurator' dataclass
  return gui_config


def check_config_file_existence(path2check: str, filename: str):
  """
  Function that raises an exception if the given path does not correspond to an
  existing file.
  """
  if (not os.path.isfile(path2check)):
    # Raise an exception
    raise FileNotFoundError("Error: missing \"" + filename + "\" configuration file")


def check_exe_file_existence(path2check: str, filename: str):
  """
  Function that raises an exception if the given path does not correspond to an
  existing executable file with right permission.
  """
  # Check the executable file existence
  check_config_file_existence(path2check, filename)
  # Check that the file has execution permission
  if (not os.access(path2check, os.X_OK)):
    # Raise an exception
    raise PermissionError("Error: the \"" + filename + "\" does not have execution permission")


def _build_nVsKn(group_file: str, group_dict: dict, search_num: str):
  """
  Function that, given the 'Group' file to read (its path), it fills up the input dictionary with:
  . keys, being the line indicating the plot 'Number'
  . values, being a list of lines indicating the available Kn-s for the corresponding plot 'Number'
  """
  # Open the given 'Group' file by specifying the ANSI encoding they are built with
  with open(group_file, 'r', encoding="cp1252") as g1:
    # Process the file line by line
    for line in g1:
      # Get the line specifying the plot 'Number'
      num = re.search(search_num, line.split('\n')[0])
      if num:
        # Declare a list holding the Kn-s of the current found 'Number'
        kns = list()
        # Get the lines specifying the Kn-s corresponding to the current found 'Number'
        while True:
          # Read the following line
          line = g1.readline()
          # Check for the presence of an empy line indicating the end of the Kn-s for the
          # current 'Number'
          if (line.isspace() or line == "end\n"):
            # Add the 'Number'-Kn entry of the dictionary
            group_dict[num.group(0)] = kns
            break
          else:
            # Add the Kn line to a list belonging to the current found 'Number'
            kns.append(line.strip())


if __name__ == "__main__":
  # Instantiate and configure the dataclass storing the GUI configuration
  gui_config = init_GuiPlotFieldsConfigurator_attrs()

  # Print the built dictionaries
  print(gui_config.groupVSnumVsKn)
  print(gui_config.sta_numVSdescription)
