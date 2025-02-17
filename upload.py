from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QLineEdit,
    QLabel,
    QScrollArea,
)
from PySide6.QtCore import QThread, Slot, Signal, Qt
from raggen import RAGDocument
import json
import os
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance, HnswConfigDiff

SETTINGS = {
    "qdrant_url": "Адрес Qdrant",
    "qdrant_key": "Ключ Qdrant",
    "sparse_model": "Sparse модель",
    "dense_model": "Dense модель"
}
NOTE = "Sparse/Dense модели для векторизации текста нельзя изменять если база данных уже создана."


# Uploading in a separate thread
class UploadThread(QThread):
    output_signal = Signal(object)

    def __init__(self, documents: list[RAGDocument], prefs):
        super().__init__()
        self.prefs = prefs
        self.documents = documents
        if not os.path.exists(prefs["fastembed_cache"]):
            os.makedirs(prefs["fastembed_cache"], exist_ok=True)
        self.client = QdrantClient(url=prefs["qdrant_url"], api_key=prefs["qdrant_key"])
        self.client.set_model(prefs["dense_model"], cache_dir=prefs["fastembed_cache"])
        self.client.set_sparse_model(prefs["sparse_model"], cache_dir=prefs["fastembed_cache"])

    def create_collections(self):
        for collection in [self.prefs["chunks_collection"], self.prefs["docs_collection"]]:
            try: 
                self.client.create_collection(
                    collection_name=collection,
                    vectors_config=self.client.get_fastembed_vector_params(),
                    sparse_vectors_config=self.client.get_fastembed_sparse_vector_params(),
                    hnsw_config=HnswConfigDiff(on_disk=True)
                )
            except:
                print(f"Collection '{collection}' already exists!")

    def run(self):
        print(self.documents)
        self.output_signal.emit("")


# Document Uploading layout
class UploadingLayout(QWidget):
    def __init__(self, preview, next, prefs):
        super().__init__()
        self.next = next
        self.preview = preview
        self.prefs = prefs

        layout = QVBoxLayout(self)

        # Middle section
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        title = QLabel("Шаг 3: Загрузка")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(title)
        note = QLabel(NOTE)
        note.setDisabled(True)
        note.setWordWrap(True)
        top_layout.addWidget(note)
        self.field_names = [x for x in SETTINGS.keys()]
        self.text_fields = {}
        for field in self.field_names:
            label = QLabel(SETTINGS[field])
            text_field = QLineEdit()
            text_field.setText(self.prefs[field])
            text_field.textChanged.connect(self.settings_changed(field))
            self.text_fields[field] = text_field
            top_layout.addWidget(label)
            top_layout.addWidget(text_field)

        scroll_area = QScrollArea()
        scroll_area.setWidget(top_section)
        scroll_area.setWidgetResizable(True)

        # Bottom section
        bottom_section = QWidget()
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.addStretch()

        self.next_button = QPushButton("Далее")
        bottom_layout.addWidget(self.next_button)
        bottom_layout.addStretch()

        # Add sections
        layout.addWidget(scroll_area)
        layout.addWidget(bottom_section)

        # Connect signals
        self.next_button.clicked.connect(self.upload)

    # Edit preferences
    def settings_changed(self, key: str):
        def wrapper(text: str):
            self.prefs[key] = text
            json.dump(self.prefs, open(self.prefs["path"], "w"))
        return wrapper

    # Convert selected file
    @Slot()
    def upload(self):
        self.setDisabled(True)
        self.preview.setReadOnly(True)
        print("Выгрузка данных...")
        documents = json.loads(self.preview.toPlainText())
        documents = [RAGDocument(**x) for x in documents]
        self.worker_thread = UploadThread(documents, self.prefs)
        self.worker_thread.output_signal.connect(self.finished)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    # Finish conversion task
    @Slot()
    def finished(self, res: str):
        self.next()
