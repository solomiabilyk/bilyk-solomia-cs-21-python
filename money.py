def transaction_generator():
    """Генератор, що по черзі повертає рядки транзакцій."""
    transactions = [
        "payment 120",
        "refund 50",
        "transfer 300",
        "invalid_format",       # Некоректний формат (буде проігноровано)
        "payment not_a_number", # Сума не є числом (буде проігноровано)
        "payment 150",
        "transfer 250"
    ]
    
    total_sum = 0
    for tx in transactions:
        yield tx
        # Парсимо валідні рядки для обчислення фінальної суми
        parts = tx.split()
        if len(parts) == 2:
            try:
                amount = float(parts[1])
                action = parts[0].lower()
                if action == 'refund':
                    total_sum -= amount
                else:
                    total_sum += amount
            except ValueError:
                pass
    return total_sum


def shadow(limit=200):
    """Параметризований декоратор для перевірки тіньового ліміту."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            gen = func(*args, **kwargs)
            accumulated = 0
            exceeded_reported = False
            
            while True:
                try:
                    item = next(gen)
                except StopIteration as e:
                    return e.value  # Повертає фінальну суму від генератора
                
                # Обробка рядка для тіньового ліміту
                parts = item.split()
                if len(parts) == 2:
                    try:
                        amount = float(parts[1])
                        action = parts[0].lower()
                        if action == 'refund':
                            accumulated -= amount
                        else:
                            accumulated += amount
                            
                        if accumulated > limit and not exceeded_reported:
                            print(f"Тіньовий ліміт перевищено. Активую схему.")
                            exceeded_reported = True
                    except ValueError:
                        pass  # Некоректні рядки ігноруються
                
                yield item
        return wrapper
    return decorator


def suspicious_counter(threshold=300):
    """Незалежний декоратор для підрахунку підозрілих сум."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            gen = func(*args, **kwargs)
            alert_triggered = False
            
            while True:
                try:
                    item = next(gen)
                except StopIteration as e:
                    return e.value
                
                parts = item.split()
                if len(parts) == 2:
                    try:
                        amount = float(parts[1])
                        # Якщо транзакція перевищує поріг
                        if amount > threshold and not alert_triggered:
                            print(f"[Suspicious Counter] Виявлено операцію, що перевищує поріг {threshold}.")
                            alert_triggered = True
                    except ValueError:
                        pass
                
                yield item
        return wrapper
    return decorator


# Навішуємо декоратори один на одного (сумісність та незалежність)
@suspicious_counter(threshold=250)
@shadow(limit=200)
def get_transactions():
    return transaction_generator()


if __name__ == "__main__":
    print("--- Початок ітерації ---")
    
    # Отримуємо обгорнутий генератор
    gen_obj = get_transactions()
    final_sum = None
    
    # Ітеруємося та виводимо кожен елемент у консоль
    while True:
        try:
            item = next(gen_obj)
            print(f"Консоль: {item}")
        except StopIteration as e:
            final_sum = e.value
            break
            
    print(f"\n--- Роботу завершено ---")
    print(f"Фінальна сума генератора: {final_sum}")