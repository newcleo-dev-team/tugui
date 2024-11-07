import os
import platform
from enum import Enum
from typing import List, Tuple, Union

from tkinter import Widget

# Flag defining the level of error management
ERROR_LEVEL: bool = 0

# List of supported OS
SUPPORTED_OS_PLATFORMS: List[str] = ["Linux", "Windows"]

# Variable storing the OS platform tugui is running on
OS_PLATFORM: str = platform.system()

# Variable storing the relative path of the icon file
ICON_PATH: Union[str, None] = None
if OS_PLATFORM == "Linux":
  ICON_PATH = "../resources/icons/tuoutgui.gif"
elif OS_PLATFORM == "Windows":
  # FIXME: to add the file "tuoutgui.ico" in the right location
  ICON_PATH = "../resources/icons/tuoutgui.ico"

def destroy_widget(widget: Widget) -> None:
  """
  Destroy the widget from the tcl/tk interpreter and
  clear out any Python object reference
  """
  if widget:
    widget.destroy()
    widget = None

class IDGA(Enum):
  """
  Enumeration storing the different types of plots (field "Type").
  """
  IDGA_1: Tuple[int, str] = (1, "1 - Different Curve Numbers")
  IDGA_2: Tuple[int, str] = (2, "2 - Different Times")
  IDGA_3: Tuple[int, str] = (3, "3 - Different Slices")

  @property
  def index(self) -> int:
    """
    Index of the element of the enumeration
    """
    return self.value[0]

  @property
  def description(self) -> str:
    """
    Descriptive string of the element of the enumeration
    """
    return self.value[1]


class IANT(Enum):
  """
  Enumeration storing the different types of IANT field.
  """
  IANT_1: Tuple[int, str] = (1, "IANT 1")
  IANT_2: Tuple[int, str] = (2, "IANT 2")
  IANT_3: Tuple[int, str] = (3, "IANT 3")

  @property
  def index(self) -> int:
    """
    Index of the element of the enumeration
    """
    return self.value[0]

  @property
  def description(self) -> str:
    """
    Descriptive string of the element of the enumeration
    """
    return self.value[1]


def check_file_existence(file_path: str) -> None:
  """
  Function for checking if the given file path exists and is a file.
  If not, the function raises an exception.
  """
  if not os.path.isfile(file_path):
    # If the file does not exists, throw an exception
    raise Exception(f"Error: file {file_path} does not exist!")

def check_file_extension_and_existence(file_path: str,
                                       file_extension: str) -> None:
  """
  Function for checking if the given file has the correct extension and
  exists. If so, True is returned; False otherwise.

  Parameters
  ----------
  file_path : str
      The path to the file to check.
  file_extension  : str
      The extension the file must have and is checked for.

  Raises
  ------
  An Exception if the file extension does not match with the required
  one or the file does not exist.
  """
  # Check the extension
  extension = os.path.splitext(file_path)
  if not (extension[1] == '.' + file_extension):
      # The file specified by the given path has not the correct extension
      raise Exception(f"The indicated file with extension '{extension[1]}' is "
                      "not valid. Please provide one with the "
                      f"'{file_extension}' extension.")
  # Check the existence
  check_file_existence(file_path)
