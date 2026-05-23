from PyQt6.QtWidgets import QApplication, QTextEdit
from PyQt6.QtGui import QTextOption
import re

class Editor(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)

        prefs = QApplication.instance().prefs

        self.base_tokens = 0
        self.textChanged.connect(self.checkTextDetails)
        self.cursorPositionChanged.connect(self.checkTextDetails)

        if prefs.get("show_tab_spaces"):
            option = QTextOption()
            option.setFlags(QTextOption.Flag.ShowTabsAndSpaces)
            option.setTabStopDistance(30)
            self.document().setDefaultTextOption(option)

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