# from tkinter import Tk
# from tkinter.filedialog import askopenfile

# Tk().withdraw()
# filename = askopenfile()
# print(filename)

import customtkinter as ctk
from customtkinter import filedialog

ctk.set_appearance_mode("dark")
def selecfile():
    filenames = filedialog.askopenfilenames()
    print(filenames)

selecfile()