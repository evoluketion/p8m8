import re
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFileDialog, QMenuBar, QSizePolicy, QToolButton, QWidget, QToolBar

class MainToolbar(QToolBar):

    def __init__(self, window_height, parent=None, editor_class=None):
        super().__init__(parent)
        self._editor_class = editor_class
        self.prefs = QApplication.instance().prefs
        self.file_opening = False

        self.setMovable(False)
        self.setFloatable(False)
        toolbar_height = int(window_height * 0.06)
        self.setFixedHeight(toolbar_height)

        # Menu bar
        self.create_menu_bar()

        spacer = MainToolbarSpacer(self)

        # Minimize button
        self.minimize_button = self.create_button("-")
        self.minimize_button.clicked.connect(self.window().showMinimized)

        # Normal button
        self.normal_button = self.create_button("■")
        self.normal_button.clicked.connect(self.window().showNormal)
        self.normal_button.setVisible(False)

        # Maximize button
        self.maximize_button = self.create_button("ロ")
        self.maximize_button.clicked.connect(self.window().showMaximized)

        # Close button
        self.close_button = self.create_button("x")
        self.close_button.clicked.connect(self.window().close)

        # Add buttons to the toolbar
        self.addWidget(spacer)
        self.addWidget(self.minimize_button)
        self.normal_action = self.addWidget(self.normal_button)
        self.maximize_action = self.addWidget(self.maximize_button)
        self.addWidget(self.close_button)
    
    def create_menu_bar(self):
        menu_bar = MenuBar(self, self._editor_class)

        self.add_file_menu()
        self.add_view_menu()

        menu_bar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.addWidget(menu_bar)

    def add_file_menu(self):
        menu_bar = self.findChild(MenuBar)
        file_menu = menu_bar.addMenu("file")

        file_menu.addAction("new")
        file_menu.addAction("open")
        file_menu.addAction("save")
        file_menu.addAction("save as")

        new_action = file_menu.actions()[0]
        new_action.setEnabled(False)  # Functionality not implemented yet, TODO
        
        open_action = file_menu.actions()[1]
        open_action.triggered.connect(menu_bar.open_file)

        save_action = file_menu.actions()[2]
        save_action.setEnabled(False)  # Functionality not implemented yet, TODO

        save_as_action = file_menu.actions()[3]
        save_as_action.triggered.connect(menu_bar.save_file_as)

        file_menu.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def add_view_menu(self):
        menu_bar = self.findChild(MenuBar)
        view_menu = menu_bar.addMenu("view")

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

    def create_button(self, text):
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

    def open_file(self):
        Editor = self._editor_class

        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Pico 8 Files (*.p8)")

        open_file_regex = [
            ('LUA',   r'__lua__(.*)\n__gfx__'),
            ('GFX',   r'__gfx__(.*)\n__label__'),
            ('LABEL', r'__label__(.*)\n__gff__'),
            ('GFF',   r'__gff__(.*)\n__map__'),
            ('MAP',   r'__map__(.*)\n__sfx__'),
            ('SFX',   r'__sfx__(.*)\n'),
        ]

        if file_name:

            self.window().tab_widget.removeTab(0)  # Remove the initial empty tab

            with open(file_name, 'r') as file:
                raw_file_content = file.read()
                sections = {}
                for name, pattern in open_file_regex:
                    match = re.search(pattern, raw_file_content, re.DOTALL)
                    sections[name] = match.group(1).strip() if match else ""

                # Have included the other sections in case I want to add features related to them in the future, but for now only the LUA section is used
                lua, gfx, label, gff, map_data, sfx = sections['LUA'], sections['GFX'], sections['LABEL'], sections['GFF'], sections['MAP'], sections['SFX']

                self.window().main_toolbar.file_opening = True
                tab_contents = lua.split("-->8") if "-->8" in lua else [lua.strip()]
                for i, content in enumerate(tab_contents):
                    editor = Editor(self)
                    stripped_content = content.strip()
                    editor.setPlainText(stripped_content)

                    tab_title = self.get_tab_name(stripped_content, file_name, i)

                    tab_layout = self.window().tab_widget.get_tab_layout(editor)

                    self.window().tab_widget.addTab(tab_layout, tab_title)

            self.window().tab_widget.tabBar().moveTab(0, self.window().tab_widget.count() - 1)  # Move the + tab to the last position
            self.window().tab_widget.setCurrentIndex(0)
            self.window().main_toolbar.file_opening = False


    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Pico 8 Files (*.p8)")
        if file_name:
            try:
                # Editor should only be able to save files as Pico 8 cartridges
                if not file_name.endswith(".p8"):
                    file_name += ".p8"
                
                with open(file_name, 'w') as f:
                    editor_text = str(self.window().tab_widget.format_file_content())
                    print(f"Saving file with content:\n{editor_text}")

                    f.write(editor_text)
                    f.close()
            except Exception as e:
                print(f"Error saving file {e}")

    def get_tab_name(self, stripped_content, file_name, i):
        first_line = stripped_content.splitlines()[0] if stripped_content else "untitled"
        comment_match = re.match(r'--\s*(.*)', first_line)
        tab_title = comment_match.group(1).strip() if comment_match else f"{file_name.split('/')[-1]}_{i}"
        return tab_title


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
