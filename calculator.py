def calculate(num1: float, num2: float, operation: str):
    if operation == '+':
        return num1 + num2
    elif operation == '-':
        return num1 - num2
    elif operation == '*':
        return num1 * num2
    elif operation == '/':
        if num2 == 0:
            return "Помилка: ділення на нуль неможливе!"
        return num1 / num2
    else:
        return "Помилка: невідома операція!"


def main():
    print("--- Простий калькулятор ---")
    
    try:
        num1 = float(input("Введіть перше число: "))
        operation = input("Введіть операцію (+, -, *, /): ").strip()
        num2 = float(input("Введіть друге число: "))
        
        result = calculate(num1, num2, operation)
        print(f"Результат: {result}")
        
    except ValueError:
        print("Помилка: введено некоректне число!")


if __name__ == "__main__":
    main()