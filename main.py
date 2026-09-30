from models import Antibiotic, Medicine, Vaccine, Vitamin


def print_medications_info(medications: list[Medicine]) -> None:
    """Функція проходить по списку й викликає info() для кожного об'єкта завдяки поліморфізму."""
    for med in medications:
        print(med.info())


if __name__ == "__main__":
    # Створюємо список різних медикаментів
    medications_list: list[Medicine] = [
        Antibiotic(name="Амоксицилін", quantity=10, price=120.0),
        Vitamin(name="Вітамін C", quantity=50, price=15.5),
        Vaccine(name="Вакцина проти грипу", quantity=5, price=450.0),
        Vitamin(name="Магній B6", quantity=20, price=85.0),
        Antibiotic(name="Азитроміцин", quantity=3, price=210.0),
    ]

    print("=== ІНФОРМАЦІЯ ПРО МЕДИКАМЕНТИ (ПОЛІМОРФІЗМ) ===\n")
    print_medications_info(medications_list)