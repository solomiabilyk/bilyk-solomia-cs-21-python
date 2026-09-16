def process_medications(batch: list[tuple]) -> list[dict]:
    results = []

    for name, quantity, category, temp in batch:
        # 1. Перевірка типів даних (quantity — int, але не bool; temp — float/int, але не bool)
        is_quantity_valid = isinstance(quantity, int) and not isinstance(quantity, bool)
        is_temp_valid = isinstance(temp, (int, float)) and not isinstance(temp, bool)

        if not is_quantity_valid or not is_temp_valid:
            temp_status = "Помилка даних"
        else:
            # 2. Перевірка температури
            if temp < 5:
                temp_status = "Надто холодно"
            elif temp > 25:
                temp_status = "Надто жарко"
            else:
                temp_status = "Норма"

        # 3. Визначення статусу категорії через match case
        match category:
            case "antibiotic":
                category_status = "Рецептурний препарат"
            case "vitamin":
                category_status = "Вільний продаж"
            case "vaccine":
                category_status = "Потребує спецзберігання"
            case _:
                category_status = "Невідома категорія"

        # 4. Формування результату
        results.append({
            "name": name,
            "category_status": category_status,
            "temp_status": temp_status
        })

    return results


# Приклад використання
if __name__ == "__main__":
    medications_batch = [
        ("Амоксицилін", 100, "antibiotic", 18.5),
        ("Вітамін C", 500, "vitamin", 2.0),
        ("Вакцина проти грипу", 50, "vaccine", 30.0),
        ("Аспірин", "десять", "vitamin", 20.0),  # Некоректна кількість
        ("Ібупрофен", 20, "painkiller", 15.0),    # Невідома категорія
    ]

    processed_batch = process_medications(medications_batch)

    for item in processed_batch:
        print(f"Препарат: {item['name']} | Категорія: {item['category_status']} | Стан температури: {item['temp_status']}")