from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from appdirs import user_config_dir, user_cache_dir
import json
import os
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QMimeData, Signal, QObject

APP_NAME = "raggen-ui"
CONFING_DIR = user_config_dir(APP_NAME)
CONFING_PATH = str((Path(CONFING_DIR) / "settings.json").absolute())
CACHE_PATH = Path(user_cache_dir(APP_NAME)) / "settings.json"


@dataclass
class AppSettings:
    app_language: str = "ru"
    file_path: str = str(Path.home().absolute())
    save_path: str = str((Path.home() / "output.json").absolute())
    raggen_cache: str = str((CACHE_PATH / "raggen").absolute())
    fastembed_cache: str = str((CACHE_PATH / "fastembed").absolute())
    chunk_size: int = 256
    languages: str = "ru"
    force_ocr: bool = True
    embed_metadata: bool = True
    include_title: bool = True
    use_llm: bool = False
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    chunks_collection: str = "raggen_chunks"
    docs_collection: str = "raggen_docs"

def save_config(config: AppSettings) -> None:
    if not os.path.exists(CONFING_PATH):
        os.makedirs(CONFING_DIR, exist_ok=True)
    json.dump(asdict(config), open(CONFING_PATH, "w"), indent=4, ensure_ascii=False)


def load_config() -> AppSettings:
    if os.path.exists(CONFING_PATH):
        return AppSettings(**json.load(open(CONFING_PATH, "r")))
    else:
        config = AppSettings()
        save_config(config)
        return config

class LoggerUI(QObject):
    log_signal = Signal(str)  # Signal to update UI

    def __init__(self, cli_output: QTextEdit):
        super().__init__()
        self.cli_output = cli_output
        self.log_signal.connect(self.append_text)  # Connect signal to method

    def write(self, text):
        if len(text.strip()) == 0:
            return
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = f"{time_str}: {text}"
        self.log_signal.emit(text)  # Emit signal instead of direct UI update

    def append_text(self, text):
        self.cli_output.append(text)
        cursor = self.cli_output.textCursor()
        self.cli_output.setTextCursor(cursor)
        self.cli_output.ensureCursorVisible()

    def flush(self):
        pass  # Needed for compatibility with sys.stdout/sys.stderr

class NoImageTextEdit(QTextEdit):
    def insertFromMimeData(self, source: QMimeData):
        if source.hasText() or source.hasHtml():
            self.insertPlainText(source.text())
