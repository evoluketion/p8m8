import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFileDialog, QMenuBar, QSizePolicy, QToolButton, QWidget, QToolBar


class MainToolbar(QToolBar):

    def __init__(self, window_height, parent=None, editor_class=None):
        super().__init__(parent)
        self._editor_class = editor_class
        self.prefs = QApplication.instance().prefs

        self.setMovable(False)
        self.setFloatable(False)
        toolbar_height = int(window_height * 0.06)
        self.setFixedHeight(toolbar_height)

        # Menu bar
        self.createMenuBar()

        spacer = MainToolbarSpacer(self)

        # Minimize button
        self.minimize_button = self.createButton("-")
        self.minimize_button.clicked.connect(self.window().showMinimized)

        # Normal button
        self.normal_button = self.createButton("■")
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)

        # Maximize button
        self.maximize_button = self.createButton("ロ")
        self.maximize_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = self.createButton("x")
        self.close_button.clicked.connect(self.window().close)

        # Add buttons to the toolbar
        self.addWidget(spacer)
        self.addWidget(self.minimize_button)
        self.normal_action = self.addWidget(self.normal_button)
        self.maximize_action = self.addWidget(self.maximize_button)
        self.addWidget(self.close_button)
    
    def createMenuBar(self):
        menuBar = MenuBar(self, self._editor_class)

        self.addFileMenu()
        self.addViewMenu()

        menuBar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.addWidget(menuBar)

    def addFileMenu(self):
        menuBar = self.findChild(MenuBar)
        file_menu = menuBar.addMenu("file")

        file_menu.addAction("new")
        file_menu.addAction("open")
        file_menu.addAction("save")
        file_menu.addAction("save as")

        new_action = file_menu.actions()[0]
        new_action.setEnabled(False)  # Functionality not implemented yet, TODO
        
        open_action = file_menu.actions()[1]
        open_action.triggered.connect(menuBar.openFile)

        save_action = file_menu.actions()[2]
        save_action.setEnabled(False)  # Functionality not implemented yet, TODO

        save_as_action = file_menu.actions()[3]
        save_as_action.triggered.connect(menuBar.saveFileAs)

        file_menu.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def addViewMenu(self):
        menuBar = self.findChild(MenuBar)
        view_menu = menuBar.addMenu("view")

        view_menu_editor_menu = view_menu.addMenu("editor")
        view_menu_editor_menu.addAction("tab spaces")
        view_menu_editor_menu.addAction("wrap text")

        tab_spaces_action = view_menu_editor_menu.actions()[0]
        tab_spaces_action.setCheckable(True)
        tab_spaces_action.setChecked(self.prefs.get("show_tab_spaces", True))
        tab_spaces_action.toggled.connect(lambda checked: self.prefs.set("show_tab_spaces", checked))

        wrap_text_action = view_menu_editor_menu.actions()[1]
        wrap_text_action.setCheckable(True)
        wrap_text_action.setChecked(self.prefs.get("wrap_text", False))
        wrap_text_action.toggled.connect(lambda checked: self.prefs.set("wrap_text", checked))

        view_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        view_menu_editor_menu.setCursor(Qt.CursorShape.PointingHandCursor)

    def createButton(self, text):
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


class MenuBar(QMenuBar):

    def __init__(self, parent=None, editor_class=None):
        super().__init__(parent)
        self._editor_class = editor_class
        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred
        )

    def openFile(self):
        Editor = self._editor_class

        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Pico 8 Files (*.p8)")

        openFileRegex = [
            ('LUA',   r'__lua__(.*)\n__gfx__'),
            ('GFX',   r'__gfx__(.*)\n__label__'),
            ('LABEL', r'__label__(.*)\n__gff__'),
            ('GFF',   r'__gff__(.*)\n__map__'),
            ('MAP',   r'__map__(.*)\n__sfx__'),
            ('SFX',   r'__sfx__(.*)\n'),
        ]

        if fileName:

            self.window().tab_widget.removeTab(0)  # Remove the initial empty tab

            with open(fileName, 'r') as file:
                rawFileContent = file.read()
                sections = {}
                for name, pattern in openFileRegex:
                    match = re.search(pattern, rawFileContent, re.DOTALL)
                    sections[name] = match.group(1).strip() if match else ""

                # Have included the other sections in case I want to add features related to them in the future, but for now only the LUA section is used
                lua, gfx, label, gff, map_data, sfx = sections['LUA'], sections['GFX'], sections['LABEL'], sections['GFF'], sections['MAP'], sections['SFX']

                self.window().total_tokens = 0
                tab_contents = lua.split("-->8") if "-->8" in lua else [lua.strip()]
                for i, content in enumerate(tab_contents):
                    editor = Editor(self)
                    strippedContent = content.strip()
                    editor.setPlainText(strippedContent)

                    tabTitle = self.getTabName(strippedContent, fileName, i)

                    tabLayout = self.window().tab_widget.getTabLayout(editor)

                    self.window().tab_widget.addTab(tabLayout, tabTitle)

            self.window().tab_widget.tabBar().moveTab(0, self.window().tab_widget.count() - 1)  # Move the + tab to the last position
            self.window().tab_widget.setCurrentIndex(0)


    def saveFileAs(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Pico 8 Files (*.p8)")
        if fileName:
            try:
                # Editor should only be able to save files as Pico 8 cartridges
                if not fileName.endswith(".p8"):
                    fileName += ".p8"
                
                with open(fileName, 'w') as f:
                    editorText = str(self.window().tab_widget.formatFileContent())
                    print(f"Saving file with content:\n{editorText}")

                    f.write(editorText)
                    f.close()
            except Exception as e:
                print(f"Error saving file {e}")

    def getTabName(self, strippedContent, fileName, i):
        firstLine = strippedContent.splitlines()[0] if strippedContent else "untitled"
        comment_match = re.match(r'--\s*(.*)', firstLine)
        tabTitle = comment_match.group(1).strip() if comment_match else f"{fileName.split('/')[-1]}_{i}"
        return tabTitle


class MainToolbarSpacer(QWidget):

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
