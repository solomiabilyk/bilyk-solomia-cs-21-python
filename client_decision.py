def process_deals(deals: list[tuple]) -> list[dict]:
    results = []

    for name, amount, status in deals:
        # 1. Перевірка типу суми (має бути int або float, але не bool, оскільки bool є підкласом int)
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            amount_category = "Фальшиві дані"
        # 2. Категоризація за сумою через if / elif / else
        elif amount < 100:
            amount_category = "Дрібнота"
        elif amount <= 999:
            amount_category = "Середнячок"
        else:
            amount_category = "Великий клієнт"

        # 3. Визначення рішення за статусом через match case
        match status:
            case "clean":
                status_decision = "Працювати без питань"
            case "suspicious":
                status_decision = "Перевірити документи"
            case "fraud":
                status_decision = "У чорний список"
            case _:
                status_decision = "Невідомий статус"

        # Формування результату для клієнта
        results.append({
            "name": name,
            "category": amount_category,
            "decision": status_decision
        })

    return results


# Тестові дані для перевірки
if __name__ == "__main__":
    deals_list = [
        ("Олексій", 50, "clean"),
        ("Марія", 450.50, "suspicious"),
        ("Іван", 1500, "fraud"),
        ("Олена", "сто тисяч", "clean"),
        ("Дмитро", 200, "unknown_status"),
        ("Анна", 1000, "clean"),
    ]

    processed_clients = process_deals(deals_list)

    # Вивід результатів
    for client in processed_clients:
        print(f"Клієнт: {client['name']} | Категорія: {client['category']} | Рішення: {client['decision']}")