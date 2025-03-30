import sys
import os

# Get the absolute path to the project's root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from PyQt5.QtWidgets import QApplication

from gui.app import App

if __name__ == "__main__":
    app = QApplication(sys.argv)
    a = App()
    a.setWindowTitle("Detector")
    a.resize(500, 500)
    a.show()
    sys.exit(app.exec_())
