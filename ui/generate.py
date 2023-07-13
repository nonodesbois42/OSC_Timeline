"""
Generate python UI files from .ui (from QtDesigner)
"""
import os

# MainWindow
os.system("pyuic6 ui/MainWindow.ui -o ui/generated/Ui_MainWindow.py")
print("MainWindow Done")
