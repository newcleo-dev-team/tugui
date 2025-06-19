import errno
import os

from enum import Enum
import shutil
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


def remove_if_file_exists(filename: str) -> None:
    """
    Function that removes the file whose path name is given as input. If no
    file actually exists at the indicated path, no exception is raised unless
    the error type is different from `ENOENT`, indicating a missing file.

    Parameters
    ----------
    filename : str
        The path name of the file to remove

    Raises
    ------
    OSError
        If the remove operation raised an `OSError` exception with type
        different from `ENOENT` (indicating a missing file).
    """
    try:
        os.remove(filename)
    except OSError as e:
        # Re-raise the exception if an error other than missing file is raised
        if e.errno != errno.ENOENT:
            raise


def _move_file_and_update_path(file_path: str, dest_folder_path: str) -> str:
    """
    Function that builds the path of the file to a destination folder and
    moves it into that.

    Parameters
    ----------
    file_path : str
        Path name to the file to move
    dest_folder_path : str
        Path name to the destination folder

    Returns
    -------
    str
        The path name of the file moved into the destination folder
    """
    # Build the file path to the destination folder
    out_output = os.path.join(
        dest_folder_path,
        os.path.basename(file_path).split(os.sep)[-1])
    # Move the file into the destination folder
    shutil.move(file_path, out_output)
    # Return the file path in the destination folder
    return out_output