import sys
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QApplication, QSizePolicy, QStyle, QToolButton, QWidget, QMainWindow, QTextEdit, QHBoxLayout, QVBoxLayout, QToolBar
from PyQt6.QtGui import QFontDatabase, QFont

class MainToolbar(QToolBar):

    def __init__(self, window_height, parent=None):
        super().__init__(parent)

        self.setMovable(False)
        self.setFloatable(False)
        toolbar_height = int(window_height * 0.06)
        self.setFixedHeight(toolbar_height)

        # File button
        self.file_button = self._make_button("file")

        spacer = Spacer(self)

        # Minimize button
        self.minimize_button = self._make_button("-")
        self.minimize_button.clicked.connect(self.window().showMinimized)

        # Normal button
        self.normal_button = self._make_button("■")
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)

        # Maximize button
        self.maximize_button = self._make_button("ロ")
        self.maximize_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = self._make_button("x")
        self.close_button.clicked.connect(self.window().close)

        # Add buttons to the toolbar
        self.addWidget(self.file_button)
        self.addWidget(spacer)
        self.addWidget(self.minimize_button)
        self.normal_action = self.addWidget(self.normal_button)
        self.maximize_action = self.addWidget(self.maximize_button)
        self.addWidget(self.close_button)

    def _make_button(self, text):
        btn = QToolButton(self)
        btn.setText(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn
    
    def window_state_changed(self, state):
        if state == Qt.WindowState.WindowMaximized:
            self.normal_action.setVisible(True)
            self.maximize_action.setVisible(False)
        else:
            self.normal_action.setVisible(False)
            self.maximize_action.setVisible(True)


class Spacer(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.window().windowHandle().startSystemMove()
        super().mousePressEvent(event)
        event.accept()


class Editor(QTextEdit):

    def __init__(self, window_height, parent=None):
        super().__init__(parent)
        self.setFixedHeight(int(window_height * 0.88))


class Footer(QToolBar):

    def __init__(self, window_height, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setFixedHeight(int(window_height * 0.06))


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

        self.main_toolbar = MainToolbar(self.screenHeight, self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)

        self.editor = Editor(self.screenHeight, self)
        self.layout.addWidget(self.editor)

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