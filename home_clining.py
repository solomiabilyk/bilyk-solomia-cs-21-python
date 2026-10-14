import os

# 1. Клас для окремого предмета на складі
class JunkItem:
    def __init__(self, name: str, quantity: int, value: float):
        self.name = name
        self.quantity = quantity
        self.value = value

    def __repr__(self):
        return f"JunkItem(name='{self.name}', quantity={self.quantity}, value={self.value})"


# 2. Інтерфейс (абстрактне сховище), що визначає правила для роботи з даними
class StorageBackend:
    def save(self, items: list[JunkItem]):
        raise NotImplementedError

    def load(self) -> list[JunkItem]:
        raise NotImplementedError


# 3. Конкретна реалізація сховища через файл (наш JunkStorage)
class FileJunkStorage(StorageBackend):
    def __init__(self, filename: str):
        self.filename = filename

    def save(self, items: list[JunkItem]):
        """Серіалізує список предметів у файл у форматі CSV з роз'єднувачем '|' та комою для дробів."""
        lines = []
        for item in items:
            # Замінюємо крапку на кому для десяткових дробів
            value_str = str(item.value).replace('.', ',')
            line = f"{item.name}|{item.quantity}|{value_str}"
            lines.append(line)
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))

    def load(self) -> list[JunkItem]:
        """Парсить файл, відновлює об'єкти та пропускає зіпсовані рядки з попередженням."""
        items = []
        if not os.path.exists(self.filename):
            return items

        with open(self.filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                # Перевірка: чи є рівно 3 поля
                if len(parts) != 3:
                    print(f"Попередження: рядок {line_num} ('{line}') пропущено — невірний формат (має бути 3 поля).")
                    continue

                name_str, qty_str, val_str = parts

                # Перевірка: чи є quantity цілим числом
                try:
                    quantity = int(qty_str)
                except ValueError:
                    print(f"Попередження: рядок {line_num} ('{line}') пропущено — кількість '{qty_str}' не є цілим числом.")
                    continue

                # Перевірка: чи є value числом з плаваючою комою (замінюємо кому назад на крапку для перетворення)
                val_str_normalized = val_str.replace(',', '.')
                try:
                    value = float(val_str_normalized)
                except ValueError:
                    print(f"Попередження: рядок {line_num} ('{line}') пропущено — ціна '{val_str}' не є числом.")
                    continue

                items.append(JunkItem(name_str, quantity, value))
        return items


# 4. Клас складу (Warehouse), який керує барахлом, але не знає деталей збереження у файл
class Warehouse:
    def __init__(self, storage: StorageBackend):
        self.storage = storage
        self.items: list[JunkItem] = self.storage.load()

    def add_item(self, item: JunkItem):
        self.items.append(item)
        self.storage.save(self.items)

    def get_item(self, name: str) -> JunkItem | None:
        for item in self.items:
            if item.name.lower() == name.lower():
                return item
        return None

    def find_items(self, query: str) -> list[JunkItem]:
        return [item for item in self.items if query.lower() in item.name.lower()]


# --- Демонстрація роботи ---
if __name__ == "__main__":
    filename = "warehouse_junk.txt"

    # Створюємо файлове сховище
    storage = FileJunkStorage(filename)

    # Передаємо сховище на склад
    my_warehouse = Warehouse(storage)

    print("--- 1. Додаємо початкові предмети та записуємо у файл ---")
    item1 = JunkItem("Бляшанка", 5, 2.5)
    item2 = JunkItem("Стара плата", 3, 7.8)
    item3 = JunkItem("Купка дротів", 10, 1.2)

    my_warehouse.add_item(item1)
    my_warehouse.add_item(item2)
    my_warehouse.add_item(item3)

    print("Предмети успішно збережено у файл.")

    print("\n--- 2. Перевіряємо читання з файлу назад ---")
    # Створимо новий склад з тим самим файлом, щоб перевірити завантаження
    reloaded_warehouse = Warehouse(FileJunkStorage(filename))
    for item in reloaded_warehouse.items:
        print(item)

    print("\n--- 3. Перевірка обробки зіпсованих рядків ---")
    # Додамо вручну у файл биті рядки для перевірки
    with open(filename, 'a', encoding='utf-8') as f:
        f.write("\nЗіпсованийПредмет|не_число|5.5") # Помилка в кількості
        f.write("\nТількиДваПоля|10")              # Мало полів
        f.write("\nНормальнийХлам|2|3,4")          # Нормальний рядок

    print("\nЗавантажуємо склад знову (очікуємо попередження):")
    test_warehouse = Warehouse(FileJunkStorage(filename))
    print("\nУспішно завантажені валідні предмети:")
    for item in test_warehouse.items:
        print(item)
    
    # Видаляємо тестовий файл після демонстрації
    if os.path.exists(filename):
        os.remove(filename)