import os

from enum import Enum
from typing import Tuple

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

def get_file_modification_time(file_path: str) -> float | None:
  """
  Function that returns the last modification time of the file whose
  path is given as input.

  Parameters
  ----------
  file_path : str
      The path of the file whose last modification time has to be
      retrieved

  Returns
  -------
  The file last modification time, if exists; None otherwise.
  """
  try:
      return os.path.getmtime(file_path)
  except OSError:
      # If the file does not exist, an OSError is caught
      return None
