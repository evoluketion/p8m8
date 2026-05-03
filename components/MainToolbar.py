import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFileDialog, QMenuBar, QSizePolicy, QToolButton, QWidget, QToolBar


class MainToolbar(QToolBar):

    def __init__(self, window_height, parent=None, editor_class=None):
        super().__init__(parent)
        self._editor_class = editor_class

        self.setMovable(False)
        self.setFloatable(False)
        toolbar_height = int(window_height * 0.06)
        self.setFixedHeight(toolbar_height)

        # Menu bar
        self.createMenuBar("file")

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

    def createMenuBar(self, text):
        menuBar = MenuBar(self, self._editor_class)
        file_menu = menuBar.addMenu(text)
        file_menu.addAction("new")
        file_menu.addAction("open")
        file_menu.addAction("save")
        file_menu.addAction("save as")

        open_action = file_menu.actions()[1]
        open_action.triggered.connect(menuBar.openFile)

        menuBar.setCursor(Qt.CursorShape.PointingHandCursor)
        file_menu.setCursor(Qt.CursorShape.PointingHandCursor)

        self.addWidget(menuBar)

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

        self.window().tab_widget.removeTab(0)  # Remove the initial empty tab

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
