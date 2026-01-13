# main.py
import sys
import os
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk
from src.ui.main_ui import SecurityScannerGUI

def main():
    root = tk.Tk()
    app = SecurityScannerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()