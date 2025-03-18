#!/usr/bin/env python
import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QLabel
)
from core import load_config
from editor import Editor
from translations import get_lang

class TabbedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.prefs = load_config()
        self.lang = get_lang(self.prefs.app_language)
       
        # Set up the main window
        self.setWindowTitle("Simple Tabbed Layout App")
        #self.setGeometry(100, 100, 300, 200)
        
        # Create a QTabWidget
        self.editor = Editor(self.prefs, self.lang)
        self.setCentralWidget(self.editor)
   
# Start app
if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TabbedApp()
    window.setWindowTitle(window.lang.title)
    window.show()

    sys.exit(app.exec())
