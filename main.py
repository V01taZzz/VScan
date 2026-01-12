#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
版本: 1.0.0
Design by V01ta
"""
import tkinter as tk
from tkinter import ttk
from src.ui.Scan_UI import SecurityScannerGUI

def main():
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use("vista")  # Windows 风格

    app = SecurityScannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


