from enum import Enum


class IDGA(Enum):
  """
  Enumeration storing the different types of plots (field "Type").
  """
  IDGA_1 = (1, "1 - Different Curve Numbers")
  IDGA_2 = (2, "2 - Different Times")
  IDGA_3 = (3, "3 - Different Slices")

  @property
  def index(self):
    """
    Index of the element of the enumeration
    """
    return self.value[0]

  @property
  def description(self):
    """
    Descriptive string of the element of the enumeration
    """
    return self.value[1]


class IANT(Enum):
  """
  Enumeration storing the different types of IANT field.
  """
  IANT_1 = (1, "IANT 1")
  IANT_2 = (2, "IANT 2")
  IANT_3 = (3, "IANT 3")

  @property
  def index(self):
    """
    Index of the element of the enumeration
    """
    return self.value[0]

  @property
  def description(self):
    """
    Descriptive string of the element of the enumeration
    """
    return self.value[1]