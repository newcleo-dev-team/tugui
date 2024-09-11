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