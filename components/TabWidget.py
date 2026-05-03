from PyQt6.QtWidgets import QTabWidget, QWidget, QHBoxLayout
from components.LineNumberArea import LineNumberArea

class TabWidget(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)

    def addTab(self, widget, title):
        super().addTab(widget, title)
        self.setCurrentWidget(widget)

    def insertTab(self, index, widget, label=""):
        return super().insertTab(index, widget, label)

    def closeTab(self, index):
        self.removeTab(index)
    
    def getTabLayout(self, editor):
        tabLayout = QHBoxLayout()
        tabLayout.setContentsMargins(0, 0, 0, 0)
        tabLayout.setSpacing(0)
        line_number_area = LineNumberArea(editor)
        tabLayout.addWidget(line_number_area)
        tabLayout.addWidget(editor)

        tabLayoutWidget = QWidget()
        tabLayoutWidget.setLayout(tabLayout)    
        return tabLayoutWidget