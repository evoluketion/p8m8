import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QTextEdit, QHBoxLayout, QVBoxLayout, QToolBar
from PyQt6.QtGui import QFontDatabase, QFont

class p8m8(QMainWindow):

    screenWidth = 800
    screenHeight = 600

    def __init__(self):
        super().__init__()

        QFontDatabase.addApplicationFont("assets/fonts/pico-8.otf")

        self.width, self.height = self.screenWidth, self.screenHeight
        self.setMinimumSize(self.width, self.height)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        with open("styles/style.qss", "r") as f:
            self.setStyleSheet(f.read())
        
        self.main_window = QWidget()
        self.layout = QHBoxLayout(self.main_window)
        self.setCentralWidget(self.main_window)

        self.init_ui()


    def init_ui(self):
        with open("styles/style.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.init_main_toolbar()

        self.init_editor()

        self.init_footer()


    def init_main_toolbar(self):
        self.main_toolbar = QToolBar("Main Toolbar")
        self.addToolBar(self.main_toolbar)

        self.main_toolbar.setMovable(False)
        self.main_toolbar.setFloatable(False)
        self.main_toolbar.setFixedHeight(int(self.screenHeight*0.06))

   
    def init_editor(self):
        self.text_edit = QTextEdit()

        self.layout.addWidget(self.text_edit)     

        self.text_edit.setFixedHeight(int(self.screenHeight*0.88))


    def init_footer(self):
        self.footer_toolbar = QToolBar("Footer Toolbar")
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.footer_toolbar)

        self.footer_toolbar.setMovable(False)
        self.footer_toolbar.setFloatable(False)
        self.footer_toolbar.setFixedHeight(int(self.screenHeight*0.06))


app = QApplication(sys.argv)
window = p8m8()
window.show()
sys.exit(app.exec())