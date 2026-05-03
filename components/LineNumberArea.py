from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtGui import QTextOption

class LineNumberArea(QTextEdit):

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.setReadOnly(True)
        self.setFixedWidth(40)
        self.setObjectName("lineNumberArea")

        option = QTextOption()
        option.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.document().setDefaultTextOption(option)
        
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.editor.textChanged.connect(self.updateLineNumbers)
        self.editor.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.updateLineNumbers()

    def updateLineNumbers(self):
        self.setPlainText("\n".join(str(i + 1) for i in range(self.editor.document().blockCount())))