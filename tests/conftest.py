import os
import sys

# This conftest.py is used to ensure pytest can find and import modules/packages from the project root.
# It is especially useful when running tests from subdirectories.

# Get the absolute path of the project root directory (one level up from the tests folder)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Print the project root for debugging purposes
print("PROJECT ROOT: ", project_root)

# Add the project root directory to sys.path so that imports like 'from backend import db_helper' work
sys.path.insert(0, project_root)
