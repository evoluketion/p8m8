import sys
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout
from PyQt6.QtGui import QFontDatabase
from components.MainToolbar import MainToolbar
from components.Editor import Editor
from components.TabWidget import TabWidget
from components.Footer import Footer


class p8m8(QMainWindow):

    screenWidth = 1280
    screenHeight = 720

    def __init__(self):
        super().__init__()
        self.total_tokens = 0

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

        self.main_toolbar = MainToolbar(self.screenHeight, self, Editor)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        self.editor = Editor(self)
        self.tab_widget = TabWidget()
        self.tab_widget.setTabsClosable(False)

        tabLayout = self.window().tab_widget.getTabLayout(self.editor)
        
        self.window().tab_widget.addTab(tabLayout, "untitled")

        self.layout.addWidget(self.tab_widget)

        self.footer = Footer(self.screenHeight, self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.footer)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.main_toolbar.window_state_changed(self.windowState())

        super().changeEvent(event)
        event.accept()


app = QApplication(sys.argv)
window = p8m8()
window.show()
sys.exit(app.exec())