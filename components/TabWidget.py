import re

from PyQt6.QtWidgets import QTabWidget, QWidget, QHBoxLayout
from components.Editor import Editor
from components.LineNumberArea import LineNumberArea

class TabWidget(QTabWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

    def close_tab(self, index):
        self.removeTab(index)

    def clear_tabs(self):
        while self.count() > 1: # Gotta be 1 so the + sign for new tabs stays there
            tab = self.widget(0)

            self.removeTab(0)

            if tab is not None:
                tab.deleteLater()
    
    def get_tab_layout(self, editor):

        line_number_area = LineNumberArea(editor)

        tab_layout = QHBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_layout.addWidget(line_number_area)
        tab_layout.addWidget(editor)

        tab_layout_widget = QWidget()
        tab_layout_widget.setLayout(tab_layout)  
        return tab_layout_widget

    def format_file_content(self):
        tab_widget_content = super().findChildren(Editor)

        file_content = ""

        # Default to version 1 if not set in prefs
        # is a ridiculously out of date version to prompt the User 
        # something is wrong with their prefs config
        pico_8_version_number = self.window().prefs.get("pico_8_version_number", 1) 
        
        file_specs_str = f"pico-8 cartridge // http://www.pico-8.com\nversion {pico_8_version_number}\n__lua__\n\n"
        gfx_str = """\n\n__gfx__
                    00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00700700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00077000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00077000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
                    00700700000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"""
        for tab in tab_widget_content:
            editor_text = tab.toPlainText()
            first_line = editor_text.splitlines()[0] if editor_text else ""
            comment_match = re.match(r'--\s*(.*)', first_line)
            if not comment_match:
                editor_text = f"--untitled\n {editor_text}"
            
            file_content = f"{file_content}\n-->8\n{editor_text}" if file_content else editor_text
    
        return file_specs_str + file_content + gfx_str.replace(" ", "")

    def handle_tab_bar_clicked(self, index):
        if index == self.count() - 1:  # If the "+" tab is clicked
            new_editor = Editor(self)
            new_tab_layout = self.get_tab_layout(new_editor)
            self.insertTab(self.count() - 1, new_tab_layout, "untitled")
            self.setCurrentIndex(self.count() - 2)  # Switch to the new tab
