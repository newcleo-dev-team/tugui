"""
Testing module for ``tugui``
"""
import os
import sys


PROJECT_PATH = os.getcwd()
SOURCE_PATH = os.path.join(
    PROJECT_PATH,"tugui"
)
sys.path.append(SOURCE_PATH)

RESOURCES_PATH = os.path.join(
    SOURCE_PATH, 'resources'
)
sys.path.append(RESOURCES_PATH)