from PyQt6.QtWidgets import QLabel, QSizePolicy, QWidget, QToolBar

class Footer(QToolBar):

    def __init__(self, window_height, parent=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.setFixedHeight(int(window_height * 0.06))

        self.line_count_label = QLabel("line 1/1", self)
        self.addWidget(self.line_count_label)

        spacer = FooterSpacer(self)

        self.addWidget(spacer)

        self.char_count_label = QLabel("0/8192", self)
        self.addWidget(self.char_count_label)


class FooterSpacer(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred
        )