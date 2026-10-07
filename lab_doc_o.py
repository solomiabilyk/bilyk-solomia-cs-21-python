from abc import ABC, abstractmethod


# 1. ІНТЕРФЕЙС ТА КЛАСИ ДОКУМЕНТІВ

class Document(ABC):
    """Абстрактний інтерфейс документа."""

    @abstractmethod
    def render(self) -> str:
        """Метод для рендерингу документа."""
        pass


class Report(Document):
    def render(self) -> str:
        return "[ЗВІТ] Форматування аналітичного звіту: підсумки, графіки та метрики."


class Invoice(Document):
    def render(self) -> str:
        return "[РАХУНОК] Форматування рахунку на оплату: реквізити, сума та ПДВ."


class Contract(Document):
    def render(self) -> str:
        return "[КОНТРАКТ] Форматування юридичного договору: сторони, умови та підписи."


class NullDocument(Document):
    """Паттерн Null Object для обробки невідомих типів документів без винятків."""

    def __init__(self, doc_type: str):
        self.doc_type = doc_type

    def render(self) -> str:
        return f"[ПОМИЛКА] Невідомий тип документа: '{self.doc_type}'. Генерація скасована."


# 2. ФАБРИКА ДОКУМЕНТІВ (Factory Pattern)

class DocumentFactory:
    """Статична фабрика для створення об'єктів документів."""

    # Реєстр типів документів у вигляді словника для уникнення if/elif
    _registry: dict[str, type[Document]] = {
        "report": Report,
        "invoice": Invoice,
        "contract": Contract,
    }

    @staticmethod
    def create(doc_type: str) -> Document:
        """Створює об'єкт відповідного документа за його строковим типом."""
        normalized_type = doc_type.strip().lower()
        
        # Отримуємо клас зі словника або повертаємо NullDocument
        doc_class = DocumentFactory._registry.get(normalized_type)
        if doc_class:
            return doc_class()
        
        return NullDocument(doc_type)


# 3. КЛІЄНТСЬКИЙ КОД

if __name__ == "__main__":
    # Список типів документів для обробки
    requested_docs = ["report", "invoice", "contract", "unknown_type", "REPORT "]

    print("=== ОБРОБКА ДОКУМЕНТІВ ЧЕРЕЗ ФАБРИКУ ===\n")

    for doc_type in requested_docs:
        # Клієнтський код робить тільки виклик фабрики й викликає render()
        document = DocumentFactory.create(doc_type)
        print(document.render())