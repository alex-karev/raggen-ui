from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QScrollArea,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QFileDialog
)
from PySide6.QtCore import Qt, Slot, QThread, Signal, QObject
from typing import Any, Callable, Optional, List
import os
from pathlib import Path
from translations import AppLanguage
from core import AppSettings, save_config

SUPPORTED_FORMATS = [".pdf", ".docx", ".doc", ".md", ".html", ".html"]

# Task thread
class TaskWorker(QObject):
    result = Signal(object)
    finished = Signal()

    def __init__(self, function: Callable):
        super().__init__()
        self.input: Any = input
        self.function: Callable = function

    @Slot(str)
    def do_work(self, input):
        output: Any = self.function(input)
        self.result.emit(output)
        self.finished.emit()


# Main control area
class EditorMenu(QWidget):
    def __init__(
        self,
        prefs: AppSettings = AppSettings(),
        lang: AppLanguage = AppLanguage(),
        preview: Optional[QTextEdit] = None,
        fields: List[str] = [],
        title: str = "Undefined",
        select: Optional[Callable] = None,
        function: Optional[Callable] = None,
        callback: Optional[Callable] = None,
    ):
        super().__init__()
        self.prefs: AppSettings = prefs
        self.lang: AppLanguage = lang
        self.preview = preview
        self.function: Callable = (
            function if function else lambda x, y,: print("Unimplemented")
        )
        self.callback: Callable = (
            callback if callback else lambda x: print("Empty callaback")
        )

        # Define layout
        layout = QVBoxLayout(self)

        # Title
        title = QLabel(title)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Twekable settins
        settings = QWidget()
        settings_layout = QVBoxLayout(settings)
        self.fields = {}
        for field in fields:
            # Special case: file input
            if field == "file":
                label = QLabel(self.lang.document)
                file_button = QPushButton(self.lang.select)
                settings_layout.addWidget(label)
                settings_layout.addWidget(file_button)
                file_button.clicked.connect(self.select_file)
                continue
            # Common case
            value = self.prefs.__getattribute__(field)
            label = QLabel(self.lang.__getattribute__(field))
            if isinstance(value, str):
                field_edit = QLineEdit()
                field_edit.setText(value)
                field_edit.textChanged.connect(self.settings_changed(field))
            elif isinstance(value, bool):
                field_edit = QCheckBox()
                field_edit.setChecked(value)
                field_edit.stateChanged.connect(self.settings_changed(field))
            elif isinstance(value, int):
                field_edit = QSpinBox()
                field_edit.setSingleStep(64)
                field_edit.setRange(0, 8192)
                field_edit.wheelEvent = lambda *event: None
                field_edit.setValue(value)
                field_edit.valueChanged.connect(self.settings_changed(field))
            settings_layout.addWidget(label)
            settings_layout.addWidget(field_edit)

        # Wrap settings into a scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidget(settings)
        scroll_area.setWidgetResizable(True)

        # Bottom section with the next button
        bottom_section = QWidget()
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.addStretch()
        self.next_button = QPushButton(self.lang.next)
        if "file" in fields:
            self.next_button.setDisabled(True)
        bottom_layout.addWidget(self.next_button)
        bottom_layout.addStretch()

        # Add sections
        layout.addWidget(title)
        layout.addWidget(scroll_area)
        layout.addWidget(bottom_section)

        # Connect next button
        self.next_button.clicked.connect(self.start_task)

    # Select file
    def select_file(self):
        file_dialog = QFileDialog(self)
        if os.path.exists(self.prefs.file_path):
            file_dialog.setDirectory(self.prefs.file_path)
        file_dialog.setWindowTitle(self.lang.document)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            filepath = Path(selected_file)
            format = filepath.suffix.lower()
            self.prefs.file_path = str(filepath.parent.absolute())
            save_config(self.prefs)
            if not format in SUPPORTED_FORMATS:
                print(self.lang.format_unsupported.format(format))
                return
            self.preview.setText(selected_file)
            self.next_button.setDisabled(False)
            print(self.lang.document_selected.format(selected_file))

    # Edit preferences
    def settings_changed(self, key: str):
        def wrapper(text: str):
            value = self.prefs.__getattribute__(key)
            if isinstance(value, int):
                new_value = int(text)
            elif isinstance(value, bool):
                new_value = value == Qt.CheckState.Checked.value
            else:
                new_value = text
            self.prefs.__setattr__(key, new_value)
            save_config(self.prefs)

        return wrapper

    # Start task
    def start_task(self):
        self.setDisabled(True)
        self.thread = QThread()
        self.worker = TaskWorker(self.function)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(
            lambda: self.worker.do_work(self.preview.toPlainText())
        )
        self.worker.finished.connect(self.thread.quit)
        self.worker.result.connect(self.finish_task)
        self.thread.start()

    # Finish task
    def finish_task(self, output: Any):
        self.setDisabled(False)
        self.callback(output)
