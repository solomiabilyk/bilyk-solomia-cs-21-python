from abc import ABC, abstractmethod


class Medicine(ABC):
    """Абстрактний базовий клас для медикаментів."""

    def __init__(self, name: str, quantity: int, price: float):
        # Перевірка типів даних у конструкторі
        if not isinstance(name, str):
            raise TypeError("Параметр 'name' має бути рядком (str).")
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise TypeError("Параметр 'quantity' має бути цілим числом (int).")
        if not isinstance(price, (int, float)) or isinstance(price, bool):
            raise TypeError("Параметр 'price' має бути числом (float/int).")

        self.name = name
        self.quantity = quantity
        self.price = float(price)

    @abstractmethod
    def requires_prescription(self) -> bool:
        """Повертає True, якщо потрібен рецепт."""
        pass

    @abstractmethod
    def storage_requirements(self) -> str:
        """Повертає умови зберігання."""
        pass

    def total_price(self) -> float:
        """Обчислює загальну вартість (за замовчуванням: quantity * price)."""
        return self.quantity * self.price

    def info(self) -> str:
        """Повертає текстову інформацію про препарат."""
        prescription_str = "Так" if self.requires_prescription() else "Ні"
        return (
            f"Препарат: {self.name} | "
            f"Кількість: {self.quantity} шт. | "
            f"Рецептурний: {prescription_str} | "
            f"Умови зберігання: {self.storage_requirements()} | "
            f"Загальна вартість: {self.total_price():.2f} грн"
        )


class Antibiotic(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "8–15°C, темне місце"


class Vitamin(Medicine):
    def requires_prescription(self) -> bool:
        return False

    def storage_requirements(self) -> str:
        return "15–25°C, сухо"


class Vaccine(Medicine):
    def requires_prescription(self) -> bool:
        return True

    def storage_requirements(self) -> str:
        return "2–8°C, холодильник"

    def total_price(self) -> float:
        # Додає 10% до загальної вартості за замовчуванням
        base_price = super().total_price()
        return base_price * 1.10