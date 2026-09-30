from abc import ABC, abstractmethod


# ==========================================
# 1. МОДЕЛІ ТРАНСПОРТУ (Базові та підкласи)
# ==========================================

class Transport(ABC):
    """Абстрактний базовий клас для транспорту."""

    def __init__(self, name: str, speed: int, capacity: int):
        if not isinstance(name, str):
            raise TypeError("Параметр 'name' має бути рядком.")
        if not isinstance(speed, int) or isinstance(speed, bool) or speed <= 0:
            raise ValueError("Параметр 'speed' має бути додатним цілим числом.")
        if not isinstance(capacity, int) or isinstance(capacity, bool) or capacity < 0:
            raise ValueError("Параметр 'capacity' має бути цілим невід'ємним числом.")

        self.name = name
        self.speed = speed
        self.capacity = capacity

    def move(self, distance: float) -> float:
        """Повертає час у дорозі у годинах (distance / speed)."""
        return distance / self.speed

    @abstractmethod
    def fuel_consumption(self, distance: float) -> float:
        """Абстрактний метод обчислення витрати пального."""
        pass

    def calculate_cost(self, distance: float, price_per_unit: float) -> float:
        """Рахує загальні витрати в грошах на основі споживання пального."""
        return self.fuel_consumption(distance) * price_per_unit

    def info(self) -> str:
        """Повертає базову інформацію про транспорт."""
        return f"Транспорт: {self.name} | Швидкість: {self.speed} км/год | Місткість: {self.capacity} осіб"


class Car(Transport):
    def fuel_consumption(self, distance: float) -> float:
        return distance * 0.07


class Bus(Transport):
    def __init__(self, name: str, speed: int, capacity: int, passengers: int = 0):
        super().__init__(name, speed, capacity)
        self.passengers = passengers

    def fuel_consumption(self, distance: float) -> float:
        if self.passengers > self.capacity:
            raise ValueError("Перевантажено!")
        return distance * 0.15


class Bicycle(Transport):
    def __init__(self, name: str, speed: int, capacity: int = 1):
        # Швидкість велосипеда обмежена 20 км/год
        actual_speed = min(speed, 20)
        super().__init__(name, actual_speed, capacity)

    def fuel_consumption(self, distance: float) -> float:
        return 0.0


class ElectricCar(Car):
    def battery_usage(self, distance: float) -> float:
        """Обчислює витрату батареї (кВт·год)."""
        return distance * 0.2

    def fuel_consumption(self, distance: float) -> float:
        """Електромобіль не використовує пальне."""
        return 0.0

    def calculate_cost(self, distance: float, price_per_unit: float) -> float:
        """Рахує вартість на основі витрати електроенергії (price_per_unit = ціна за кВт·год)."""
        return self.battery_usage(distance) * price_per_unit


# ==========================================
# 2. ФУНКЦІЯ ОБРОБКИ ТА ВИКОНАННЯ КОДУ
# ==========================================

def display_transports_summary(transports: list[Transport], distance: float = 100.0) -> None:
    """Виводить назву, час у дорозі на вказану відстань та витрати пального."""
    print(f"=== ЗВІТ ДЛЯ ПОЇЗДКИ НА {distance} км ===\n")
    
    for t in transports:
        time_in_hours = t.move(distance)
        
        try:
            fuel = t.fuel_consumption(distance)
            fuel_str = f"{fuel:.2f} л" if fuel > 0 else "0 (не використовує)"
        except ValueError as err:
            fuel_str = f"Помилка: {err}"

        print(f"• {t.name}:")
        print(f"   - Час у дорозі: {time_in_hours:.2f} год.")
        print(f"   - Витрати пального: {fuel_str}")
        print("-" * 40)


if __name__ == "__main__":
    # Створюємо список різних видів транспорту
    fleet: list[Transport] = [
        Car(name="Toyota Corolla", speed=100, capacity=5),
        Bus(name="Міський Автобус №1", speed=50, capacity=30, passengers=25),
        Bus(name="Переповнений Автобус", speed=40, capacity=20, passengers=25),  # Викличе "Перевантажено!"
        Bicycle(name="Міський Велосипед", speed=25, capacity=1),                 # Швидкість обмежиться до 20 км/год
        ElectricCar(name="Tesla Model 3", speed=120, capacity=5)
    ]

    # Виклик функції для виведення результатів
    display_transports_summary(fleet, distance=100.0)

    # Розрахунок вартості для Tesla
    tesla = fleet[-1]
    cost = tesla.calculate_cost(distance=100.0, price_per_unit=4.32)  # 4.32 грн за кВт·год
    print(f"\nВартість зарядки Tesla на 100 км: {cost:.2f} грн")