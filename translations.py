from dataclasses import dataclass

@dataclass
class AppLanguage:
    title: str = "RAGGen UI"
    chunk_size: str = "Chunk Size"
    languages: str = "Languages"
    force_ocr: str = "Force OCR"
    use_llm: str = "Use LLM"
    llm_base_url: str = "LLM API URL"
    llm_api_key: str = "LLM API Key"
    llm_model: str = "LLM Model Name"
    qdrant_url: str = "Qdrant URL"
    qdrant_key: str = "Qdrant Kay"
    sparse_model: str = "Sparse Encoder"
    dense_model: str = "Dense Encoder"
    preview: str = "Preview"
    select: str = "Select"
    document: str = "Document"
    format_unsupported: str = "Format '{}' is not supported"
    document_selected: str = "Document selected: {}"
    next: str = "Next"
    preprocess_step: str = "Step 1. Convertion"
    split_step: str = "Step 2. Processing"
    upload_step: str = "Step 3. Uploading"
    upload_note: str = "WARNING! You can't change sparse/dense encoder models after the collection was created"

def get_lang(lang: str) -> AppLanguage:
    if lang == "ru":
        return AppLanguage(
            chunk_size = "Размер чанка",
            languages = "Языки",
            force_ocr = "Принудительный OCR",
            use_llm = "Использовать LLM",
            llm_base_url = "URL API LLM",
            llm_api_key = "Ключ API LLM",
            llm_model = "Название модели LLM",
            qdrant_url = "URL Qdrant",
            qdrant_key = "Ключ Qdrant",
            sparse_model = "Sparse кодировщик",
            dense_model = "Dense кодировщик",
            preview = "Предосмотр",
            select = "Выбрать",
            document = "Документ",
            format_unsupported = "Формат '{}' не поддерживается",
            document_selected = "Выбран документ: {}",
            next = "Далее",
            preprocess_step = "Шаг 1. Преобразование",
            split_step = "Шаг 2. Обработка",
            upload_step = "Шаг 3. Загрузка",
            upload_note = "ВНИМАНИЕ! Вы не можете изменить модели кодировщиков после создания коллекции",
        )
    else:
        return AppLanguage()

