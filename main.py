# main.py
import sys
import os
from pathlib import Path
from src.ui.main_ui import MainGUI
import tkinter as tk

if __name__ == "__main__":
    root = tk.Tk()
    app = MainGUI(root)
    root.mainloop()