import tkinter as tk
from tkinter import filedialog

def pick_directory():
    """
    Opens a dialog for the user to pick a directory.
    Returns the selected directory path or None if canceled.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    directory = filedialog.askdirectory(title="Select a directory with images")
    return directory
