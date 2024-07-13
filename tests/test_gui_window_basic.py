import os
import sys
from tkinter import TclError
import unittest

from tugui.main import TuPostProcessingGui

class TestGUI(unittest.TestCase):
    """
    """

    def test_01_gui_building_no_exec(self):
        """
        """
        print("#-------------------------------------")
        print("'TuPostProcessingGui' tests started:")
        print("Checking initial setup...")
        # Instantiate the GUI class
        try:
            print(" -> test_gui_building_no_exec: ", end="")
            self.root = TuPostProcessingGui("GUI Window", 300, 150)
        except Exception as e:
            print("successful")


if __name__ == '__main__':
    unittest.main(verbosity=2)