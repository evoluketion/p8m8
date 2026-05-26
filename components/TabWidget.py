import re

from PyQt6.QtWidgets import QTabWidget, QWidget, QHBoxLayout
from components.Editor import Editor
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

    def formatFileContent(self):
        tabWidgetContent = super().findChildren(Editor)

        fileContent = ""

        # Default to version 1 if not set in prefs
        # is a ridiculously out of date version to prompt the User 
        # something is wrong with their prefs config
        pico8VersionNumber = self.window().prefs.get("pico_8_version_number", 1) 
        
        fileSpecsStr = f"pico-8 cartridge // http://www.pico-8.com\nversion {pico8VersionNumber}\n__lua__\n\n"
        gfxStr = """\n\n__gfx__
                    00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00700700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00077000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00077000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00700700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"""
        for tab in tabWidgetContent:
            editorText = tab.toPlainText()
            firstLine = editorText.splitlines()[0] if editorText else ""
            comment_match = re.match(r'--\s*(.*)', firstLine)
            if not comment_match:
                editorText = f"--untitled\n {editorText}"
            
            fileContent = f"{fileContent}\n-->8\n{editorText}" if fileContent else editorText
    
        return fileSpecsStr + fileContent + gfxStr.replace(" ", "")

    def handleTabBarClicked(self, index):
        if index == self.count() - 1:  # If the "+" tab is clicked
            newEditor = Editor(self)
            newTabLayout = self.getTabLayout(newEditor)
            self.insertTab(self.count() - 1, newTabLayout, "untitled")
            self.setCurrentIndex(self.count() - 2)  # Switch to the new tab
