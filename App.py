import re
import sys
from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtWidgets import QApplication, QFileDialog, QLabel, QMenuBar, QSizePolicy, QStyle, QTabWidget, QToolButton, QWidget, QMainWindow, QTextEdit, QHBoxLayout, QVBoxLayout, QToolBar
from PyQt6.QtGui import QFontDatabase, QFont, QTextOption

class MainToolbar(QToolBar):

    def __init__(self, window_height, parent=None):
        super().__init__(parent)

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
        menuBar = MenuBar(self)
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


class MenuBar(QMenuBar):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred
        )
    
    def openFile(self):

        fileName, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Pico 8 Files (*.p8)")

        openFileRegex = [
            ('LUA',       r'__lua__(.*)\n__gfx__'),
            ('GFX',       r'__gfx__(.*)\n__label__'),
            ('LABEL',     r'__label__(.*)\n__gff__'),
            ('GFF',       r'__gff__(.*)\n__map__'),
            ('MAP',       r'__map__(.*)\n__sfx__'),
            ('SFX',       r'__sfx__(.*)\n'),
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
                    
                    tabLayout = QHBoxLayout()
                    tabLayout.setContentsMargins(0, 0, 0, 0)
                    tabLayout.setSpacing(0)
                    line_number_area = LineNumberArea(editor)
                    tabLayout.addWidget(line_number_area)
                    tabLayout.addWidget(editor)

                    tabLayoutWidget = QWidget()
                    tabLayoutWidget.setLayout(tabLayout)
                    
                    self.window().tab_widget.addTab(tabLayoutWidget, tabTitle)
        
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


class Editor(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_tokens = 0
        self.textChanged.connect(self.checkTextDetails)
        self.cursorPositionChanged.connect(self.checkTextDetails)

    def checkTextDetails(self):
        text = self.toPlainText()
        current = self.processTokens(text)
        delta = current - self.base_tokens
        self.base_tokens = current
        self.window().total_tokens += delta
        self.window().footer.char_count_label.setText(f"{self.window().total_tokens}/8192")

        current_line = self.textCursor().blockNumber() + 1
        line_count = text.count("\n") + 1
        self.window().footer.line_count_label.setText(f"line {current_line}/{line_count}")

    def processTokens(self, text):
        token_patterns = [
            ('COMMENT',       r'--[^\n]*'),
            ('STRING',        r'"[^"]*"|\'[^\']*\''),
            ('NUMBER',        r'0x[0-9a-f]*\.?[0-9a-f]*|[0-9]+\.?[0-9]*'),
            ('OP',            r'!=|~=|<=|>=|\.\.|->?>?|//|<<|>>|[+\-*/%^&|~<>=!]=?|\\'),
            ('KEYWORD',       r'\b(?:if|then|else|elseif|while|do|for|in|return|'
                              r'function|repeat|until|break|not|and|or|true|false|nil)\b'),
            ('KW_FREE',       r'\b(?:end|local)\b'),
            ('IDENT',         r'[a-z_][a-z0-9_]*'),
            ('OPEN_BRACKET',  r'[(\[{]'),
            ('CLOSE_BRACKET', r'[)\]}]'),
            ('PUNCT_FREE',    r'[,;.:]'),
            ('SKIP',          r'\s+'),
        ]

        master = re.compile(
            '|'.join(f'(?P<{name}>{pat})' for name, pat in token_patterns),
            re.DOTALL
        )

        number_re = re.compile(
            r'0[x][0-9a-f]*\.?[0-9a-f]*|[0-9]+\.?[0-9]*',
            re.IGNORECASE
        )

        FREE = {'COMMENT', 'KW_FREE', 'CLOSE_BRACKET', 'PUNCT_FREE', 'SKIP'}
        OPERAND_KINDS = {'NUMBER', 'STRING', 'IDENT', 'CLOSE_BRACKET'}

        token_count = 0
        prev_kind = None
        pos = 0

        while pos < len(text):
            m = master.match(text, pos)
            if not m:
                pos += 1
                continue
            
            # if kind == 'COMMENT' and 

            kind = m.lastgroup
            value = m.group()
            pos = m.end()

            if kind == 'SKIP':
                continue

            if kind == 'OP' and value in ('-', '~') and prev_kind not in OPERAND_KINDS:
                num_match = number_re.match(text, pos)
                if num_match:
                    token_count += 1  # merged -3 counts as 1 token
                    prev_kind = 'NUMBER'
                    pos = num_match.end()
                    continue

            if kind not in FREE:
                token_count += 1
            
            prev_kind = kind

        return token_count
    
    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        for action in menu.actions():
            action.setText(action.text().lower())
        menu.exec(event.globalPos())


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


class p8m8(QMainWindow):

    screenWidth = 800
    screenHeight = 600

    def __init__(self):
        super().__init__()
        self.total_tokens = 0

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

        self.editor = Editor(self)
        self.tab_widget = TabWidget()
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.addTab(self.editor, "untitled")
        self.layout.addWidget(self.tab_widget)

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