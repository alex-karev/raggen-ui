from PySide6.QtWidgets import (
    QWidget,
    QTextEdit,
    QSplitter,
    QLabel,
    QVBoxLayout,
    QStackedLayout,
    QPushButton
)
from PySide6.QtCore import Qt, Signal, QThread, QObject
import sys, json
from pathlib import Path
from core import NoImageTextEdit, LoggerUI
from menu import EditorMenu
from raggen import RAGGen


class Editor(QWidget):
    text_ready = Signal(str)  # Signal to update QTextEdit safely

    def __init__(self, prefs, lang):
        super().__init__()
        self.current_index = 0
        self.prefs = prefs
        self.lang = lang
        self.filename = "Unknown"

        # Main layout
        layout = QVBoxLayout(self)

        # Right pane (editable text)
        self.preview = NoImageTextEdit()
        self.preview.setPlaceholderText(self.lang.preview)
        self.preview.setReadOnly(True)

        # Left pane
        left_pane = QSplitter(orientation=Qt.Vertical)
        left_pane.setContentsMargins(2, 2, 2, 2)

        # Top-left area (menu)
        menu = QWidget()
        self.menu_layout = QStackedLayout(menu)

        # Define menu steps
        self.convert_step = EditorMenu(
            self.prefs,
            self.lang,
            self.lang.preprocess_step,
            [
                "file",
                "languages",
                "force_ocr",
                "use_llm",
                "llm_base_url",
                "llm_api_key",
                "llm_model",
            ],
            self.convert,
        )
        self.split_step = EditorMenu(
            self.prefs,
            self.lang,
            self.lang.split_step,
            ["chunk_size", "embed_metadata", "include_title"],
            self.split,
        )
        save_step = EditorMenu(
            self.prefs,
            self.lang,
            self.lang.split_step,
            ["save"],
            self.split,
        )
        self.menu_layout.addWidget(self.convert_step)
        self.menu_layout.addWidget(self.split_step)
        self.menu_layout.addWidget(save_step)
        back_button = QPushButton(self.lang.back)
        back_button.clicked.connect(self.back)
        done_menu = QWidget()
        done_layout = QVBoxLayout(done_menu)
        done_layout.addWidget(QLabel(text=self.lang.done))
        done_layout.addWidget(back_button)
        self.menu_layout.addWidget(done_menu)
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

        # Add bottom label to layout
        bottom_label = QLabel('Made by <a href="https://github.com/alex-karev/raggen-ui">Alex Karev</a>')
        bottom_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        bottom_label.setFixedHeight(20)
        layout.addWidget(bottom_label)

        # Connect signal
        self.text_ready.connect(self.preview.setText)
        self.convert_step.file_selected.connect(self.text_ready.emit)
        self.convert_step.task_started.connect(self.convert)
        self.split_step.task_started.connect(self.split)
        save_step.file_saved.connect(self.save)

    def next(self):
        """Move to next step in menu"""
        self.current_index += 1
        self.menu_layout.setCurrentIndex(self.current_index)

    def convert(self):
        """Convert texts with RAG and update UI safely"""
        input_text = self.preview.toPlainText()
        self.filename = Path(input_text).stem
        print(self.lang.preprocessing)
        self.run_task(self._convert_task, input_text)

    def split(self):
        """Split texts with RAG and update UI safely"""
        input_text = self.preview.toPlainText()
        print(self.lang.splitting)
        self.run_task(self._split_task, input_text)

    def save(self, path):
        """Save splitted texts into a file"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.preview.toPlainText())
        print(self.lang.save_path.format(path))
        self.next()

    def back(self):
        """Go back to step 1"""
        self.convert_step.next_button.setDisabled(True)
        self.convert_step.file_button.setDisabled(False)
        self.split_step.next_button.setDisabled(False)
        self.current_index = 0
        self.menu_layout.setCurrentIndex(0)

    def run_task(self, task_function, input_text):
        """Run a long task in a separate thread and update UI safely"""
        self.worker_thread = QThread()
        self.worker = Worker(task_function, input_text)
        self.worker.moveToThread(self.worker_thread)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.result.connect(self.text_ready.emit)
        self.worker.result.connect(self.next)
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

    def _convert_task(self, input_text):
        rag = RAGGen(
            languages=self.prefs.languages,
            force_ocr=self.prefs.force_ocr,
            llm_for_headings=self.prefs.use_llm,
            base_url=self.prefs.llm_base_url,
            api_key=self.prefs.llm_api_key,
            model=self.prefs.llm_model,
        )
        text = rag._convert_file(input_text)
        return rag._preprocess_markdown_text(text)

    def _split_task(self, input_text):
        rag = RAGGen(
            chunk_size=self.prefs.chunk_size,
            embed_meta=self.prefs.embed_metadata,
            field_names={
                "title": "Title",
                "section": "Section",
                "subsection": "Subsection",
                "paragraph": "Paragraph",
            },
        )
        splits = rag._split_markdown_text(
            input_text,
            metadata={"title": self.filename} if self.prefs.include_title else {},
        )
        for split in splits:
            if not split.metadata:
                split.metadata = {}
            split.metadata["length"] = split.length
        return json.dumps(
            [{"document": x.text, "metadata": x.metadata} for x in splits],
            ensure_ascii=False,
            indent=4,
        )


class Worker(QObject):
    result = Signal(str)
    finished = Signal()

    def __init__(self, function, input_text):
        super().__init__()
        self.function = function
        self.input_text = input_text

    def run(self):
        output = self.function(self.input_text)
        self.result.emit(output)
        self.finished.emit()
