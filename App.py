import sys
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QHBoxLayout
from PyQt6.QtGui import QFontDatabase
from components.MainToolbar import MainToolbar
from components.Editor import Editor
from components.TabWidget import TabWidget
from components.Footer import Footer
from config.prefs import Prefs


class p8m8(QMainWindow):

    def __init__(self):

        self.prefs = Prefs()
        self.screen_width = 1280
        self.screen_height = 720

        super().__init__()

        QFontDatabase.addApplicationFont("assets/fonts/pico-8.otf")

        self.width, self.height = self.screen_width, self.screen_height
        self.setMinimumSize(self.width, self.height)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        with open("styles/style.qss", "r") as f:
            self.setStyleSheet(f.read())
        
        self.main_window = QWidget()
        self.layout = QHBoxLayout(self.main_window)
        self.setCentralWidget(self.main_window)

        self.init_ui()

    def init_ui(self):
        with open("styles/style.qss", "r") as f:
            self.setStyleSheet(f.read())

        self.main_toolbar = MainToolbar(self.screen_height, self, Editor)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        self.editor = Editor(self)
        self.tab_widget = TabWidget()
        self.tab_widget.setTabsClosable(False)

        tab_layout = self.window().tab_widget.get_tab_layout(self.editor)
        
        self.window().tab_widget.addTab(tab_layout, "untitled")
        self.window().tab_widget.addTab(QWidget(), "+")
        self.window().tab_widget.tabBarClicked.connect(self.window().tab_widget.handle_tab_bar_clicked)

        self.layout.addWidget(self.tab_widget)
        self.window().tab_widget.setCurrentIndex(0)

        self.footer = Footer(self.screen_height, self)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.footer)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            self.main_toolbar.window_state_changed(self.windowState())

        super().changeEvent(event)
        event.accept()


QApplication.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar)
app = QApplication(sys.argv)
app.prefs = Prefs()
window = p8m8()
window.show()
sys.exit(app.exec())