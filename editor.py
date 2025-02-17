from PySide6.QtWidgets import (
    QWidget,
    QTextEdit,
    QSplitter,
    QLabel,
    QVBoxLayout,
    QStackedLayout,
)
from PySide6.QtCore import Qt
import sys
from core import NoImageTextEdit, LoggerUI
from menu import EditorMenu
from raggen import RAGGen


def a(input):
    print("Kurwa bober")
    return "f"


def b(input):
    print(input, "is ok")


class Editor(QWidget):
    def __init__(self, prefs, lang):
        super().__init__()
        self.current_index = 0
        self.prefs = prefs
        self.lang = lang

        # Main layout
        layout = QVBoxLayout(self)

        # Right pane (editable text)
        self.preview = NoImageTextEdit()
        self.preview.setPlaceholderText(self.lang.preview)
        self.preview.setReadOnly(True)

        # Left pane
        left_pane = QSplitter(orientation=Qt.Vertical)
        left_pane.setContentsMargins(2, 2, 2, 2)

        # Top-left area (buttons)
        menu = QWidget()
        done2 = QLabel(text="Done2")
        self.menu_layout = QStackedLayout()
        self.menu_layout.addWidget(
            EditorMenu(
                prefs=self.prefs,
                lang=self.lang,
                preview=self.preview,
                fields=["file", "languages", "force_ocr"],
                title=self.lang.preprocess_step,
                function=self.convert,
                callback=self.next
            )
        )
        self.menu_layout.addWidget(
            EditorMenu(
                self.prefs,
                self.lang,
                self.preview,
                ["chunk_size", "use_llm"],
                self.lang.preprocess_step,
                function=a,
                callback=b,
            )
        )
        self.menu_layout.addWidget(done2)
        self.current_index = 0
        self.menu_layout.setCurrentIndex(self.current_index)
        menu.setLayout(self.menu_layout)

        # Bottom-left area (CLI output)
        cli_output = QTextEdit()
        cli_output.setReadOnly(True)
        sys.stdout = LoggerUI(cli_output)
        sys.stderr = LoggerUI(cli_output)

        # Add left area widgets
        left_pane.addWidget(menu)
        left_pane.addWidget(cli_output)

        # Add left and right panes to the main layout
        splitter = QSplitter()
        splitter.addWidget(left_pane)
        splitter.addWidget(self.preview)
        layout.addWidget(splitter)

    # Switch to next step
    def next(self, output):
        self.current_index += 1
        self.menu_layout.setCurrentIndex(self.current_index)

    # Convert texts
    def convert(self, input):
        rag = RAGGen(
            cache_dir=self.prefs.raggen_cache,
            languages=self.prefs.languages,
            force_ocr=self.prefs.force_ocr
        )
        text = rag._convert_file(input)
        text = rag._preprocess_markdown_text(text)
        self.preview.setText(text)


