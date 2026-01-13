#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同源资产侦察助手 - VScan
版本: 1.0.0
Design by V01ta
"""
import sys
import os
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from src.ui.main_ui import SecurityScannerGUI

def main():
    root = tk.Tk()
    app = SecurityScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()