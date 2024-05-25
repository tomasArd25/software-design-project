from cx_Freeze import setup, Executable
import sys
import os
import PyQt5

# Include necessary files
include_files = [
    r'C:\Users\PERSONAL\Videos\GoalShit\FinalsProject\Deployment\places_data.db',  # Add any additional files or directories here
]

# Find the include files for PyQt5
PYQT5_DIR = os.path.dirname(PyQt5.__file__)
PLATFORM_DIR = os.path.join(PYQT5_DIR, 'Qt', 'plugins', 'platforms')

# Check if the platform directory exists and include it
if os.path.exists(PLATFORM_DIR):
    include_files.append((PLATFORM_DIR, 'platforms'))

# Define build options
build_options = {
    'packages': ['sys', 'sqlite3', 'bcrypt', 'pandas', 'matplotlib', 'PyQt5.QtCore', 'PyQt5.QtWidgets'],
    'excludes': ['PyQt6', 'PySide6'],
    'include_files': include_files,
}

# Specify the base. If your application is a GUI, use 'Win32GUI' instead of 'console' or None
base = 'Win32GUI' if sys.platform == 'win32' else None

# Define the executables
executables = [
    Executable(
        'main.py',
        base=base,
        target_name='Information System',
        icon=r'C:\Users\PERSONAL\Videos\GoalShit\FinalsProject\Deployment\app_icon\pngegg.ico'  # Specify the path to your icon file here
    )
]

# Setup the application
setup(
    name='Information System',
    version='1.0',
    description='First final prototype',
    options={'build_exe': build_options},
    executables=executables
)
