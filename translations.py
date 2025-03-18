from dataclasses import dataclass

@dataclass
class AppLanguage:
    title: str = "RAGGen UI"
    chunk_size: str = "Chunk Size"
    languages: str = "Languages"
    force_ocr: str = "Force OCR"
    embed_metadata: str = "Embed metadata"
    include_title: str = "Include title"
    use_llm: str = "Use LLM"
    llm_base_url: str = "LLM API URL"
    llm_api_key: str = "LLM API Key"
    llm_model: str = "LLM Model Name"
    preview: str = "Preview"
    select: str = "Select"
    document: str = "Document"
    format_unsupported: str = "Format '{}' is not supported"
    document_selected: str = "Document selected: {}"
    next: str = "Next"
    preprocess_step: str = "Step 1. Convertion"
    split_step: str = "Step 2. Processing"
    save_step: str = "Step 3. Saving"
    preprocessing: str = "Preprocessing..."
    splitting: str = "Splitting..."
    save: str = "Save"
    save_as: str = "Save as"
    save_path: str = "File saved to: {}"
    done: str = "Done!"
    back: str = "Back"

def get_lang(lang: str) -> AppLanguage:
    if lang == "ru":
        return AppLanguage(
            chunk_size = "Размер чанка",
            languages = "Языки",
            force_ocr = "Принудительный OCR",
            embed_metadata = "Встроить метаданные",
            include_title = "Сохранить название",
            use_llm = "Использовать LLM",
            llm_base_url = "URL API LLM",
            llm_api_key = "Ключ API LLM",
            llm_model = "Название модели LLM",
            preview = "Предосмотр",
            select = "Выбрать",
            document = "Документ",
            format_unsupported = "Формат '{}' не поддерживается",
            document_selected = "Выбран документ: {}",
            next = "Далее",
            preprocess_step = "Шаг 1. Преобразование",
            split_step = "Шаг 2. Обработка",
            save_step = "Шаг 3. Сохранение",
            preprocessing = "Предобработка...",
            splitting = "Разделение на чанки...",
            save = "Сохранить",
            save_as = "Сохранить как",
            save_path = "Файл сохранён в: {}",
            done = "Готово!",
            back = "Назад"
        )
    else:
        return AppLanguage()

