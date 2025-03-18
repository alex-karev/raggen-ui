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
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path
import os
from core import AppSettings, save_config

SUPPORTED_FORMATS = [".pdf", ".docx", ".md", ".html"]


class EditorMenu(QWidget):
    task_started = Signal()  # Signal to trigger processing
    file_selected = Signal(str)  # Signal to trigger file selection
    file_saved = Signal(str)  # Signal to trigger file save

    def __init__(
        self, prefs: AppSettings, lang, title: str, fields: list[str], function
    ):
        super().__init__()
        self.prefs = prefs
        self.lang = lang
        self.function = function
        self.selected_file = ""
        self.save_file = ""

        # Layout setup
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Settings section
        self.fields = {}
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)

        # File selector
        if "file" in fields:
            self.file_button = QPushButton(self.lang.select)
            self.file_button.clicked.connect(self.select_file)
            settings_layout.addWidget(QLabel(self.lang.document))
            settings_layout.addWidget(self.file_button)

        # "Save" button if "save" field is in fields
        if "save" in fields:
            self.save_button = QPushButton(self.lang.save)
            self.save_button.clicked.connect(self.save_file_dialog)
            settings_layout.addWidget(self.save_button)

        # Preferences
        for field in fields:
            if field in ["file", "save"]:
                continue
            value = prefs.__getattribute__(field)
            if isinstance(value, int) and not isinstance(value, bool):
                self.create_setting(settings_layout, field, QSpinBox, 64, 0, 8192)
            elif isinstance(value, bool):
                self.create_setting(settings_layout, field, QCheckBox)
            else:
                self.create_setting(settings_layout, field, QLineEdit)

        # Scrollable settings area
        scroll_area = QScrollArea()
        scroll_area.setWidget(settings_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Bottom section with "Next" button
        bottom_section = QWidget()
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.addStretch()
        if not "save" in fields:
            self.next_button = QPushButton(self.lang.next)
            if "file" in fields:
                self.next_button.setDisabled(True)  # Enabled after file selection
            self.next_button.clicked.connect(self.start_task)
            bottom_layout.addWidget(self.next_button)
        bottom_layout.addStretch()
        layout.addWidget(bottom_section)

    def create_setting(self, layout, key, widget_class, step=1, min_val=0, max_val=100):
        """Dynamically creates UI elements for settings"""
        label = QLabel(self.lang.__getattribute__(key))
        layout.addWidget(label)

        if widget_class == QSpinBox:
            widget = QSpinBox()
            widget.setSingleStep(step)
            widget.setRange(min_val, max_val)
            widget.setValue(getattr(self.prefs, key, 0))
            widget.valueChanged.connect(
                lambda value: self.update_preference(key, value)
            )
        elif widget_class == QCheckBox:
            widget = QCheckBox()
            widget.setChecked(getattr(self.prefs, key, False))
            widget.stateChanged.connect(
                lambda state: self.update_preference(key, bool(state))
            )
        elif widget_class == QLineEdit:
            widget = QLineEdit()
            widget.setText(getattr(self.prefs, key, ""))
            widget.textChanged.connect(lambda text: self.update_preference(key, text))

        layout.addWidget(widget)
        self.fields[key] = widget

    def select_file(self):
        """Open file dialog and validate selection"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle(self.lang.document)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if os.path.exists(self.prefs.file_path):
            file_dialog.setDirectory(self.prefs.file_path)

        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            filepath = Path(selected_file)
            if filepath.suffix.lower() not in SUPPORTED_FORMATS:
                print(self.lang.format_unsupported.format(filepath.suffix))
                return

            self.selected_file = str(filepath)
            self.update_preference("file_path", str(Path(self.selected_file).parent.absolute()))
            self.next_button.setDisabled(False)  # Enable processing
            print(self.lang.document_selected.format(self.selected_file))
        self.file_selected.emit(self.selected_file)

    def save_file_dialog(self):
        """Open save file dialog and emit file_saved signal"""
        save_dialog = QFileDialog(self)
        save_dialog.setWindowTitle(self.lang.save_as)
        save_dialog.setFileMode(QFileDialog.AnyFile)
        
        default_filename = self.prefs.save_path
        save_dialog.setDefaultSuffix(".json")
        save_dialog.selectFile(default_filename)

        if save_dialog.exec():
            save_path = save_dialog.selectedFiles()[0]
            if save_path:
                self.save_file = save_path
                self.update_preference("save_path", self.save_file)
                self.file_saved.emit(self.save_file)  # Emit the file_saved signal

    def update_preference(self, key, value):
        """Update settings and save configuration"""
        setattr(self.prefs, key, value)
        save_config(self.prefs)

    def start_task(self):
        """Emit signal to trigger processing in main editor"""
        self.next_button.setDisabled(True)
        if hasattr(self, "file_button"):
            self.file_button.setDisabled(True)
        self.task_started.emit()
