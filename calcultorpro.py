import re


def tokenize(expression: str) -> list[str]:
    """Розбиває рядок на окремі токени (числа, оператори, дужки)."""
    # Шаблон знаходить числа (включаючи дробові) або окремі символи +, -, *, /, (, )
    pattern = r'\d+(?:\.\d+)?|[+\-*/()]'
    return re.findall(pattern, expression)


def shunting_yard(tokens: list[str]) -> list[str]:
    """Перетворює токени із інфіксного запису в зворотний польський (RPN)."""
    output = []
    stack = []
    
    precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2
    }
    
    for token in tokens:
        if re.match(r'^\d+(?:\.\d+)?$', token):
            output.append(token)
        elif token in precedence:
            while stack and stack[-1] in precedence and precedence[stack[-1]] >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if not stack:
                raise ValueError("Небалансовані дужки: відсутня відкриваюча дужка '('")
            stack.pop()  # Видаляємо '(' зі стеку

    while stack:
        op = stack.pop()
        if op in '()':
            raise ValueError("Небалансовані дужки: відсутня закриваюча дужка ')'")
        output.append(op)
        
    return output


def evaluate_rpn(rpn_tokens: list[str]) -> float:
    """Обчислює значення виразу, записаного в RPN."""
    stack = []
    
    for token in rpn_tokens:
        if re.match(r'^\d+(?:\.\d+)?$', token):
            stack.append(float(token))
        else:
            if len(stack) < 2:
                raise ValueError("Некоректний математичний вираз")
            b = stack.pop()
            a = stack.pop()
            
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            elif token == '/':
                if b == 0:
                    raise ZeroDivisionError("Ділення на нуль неможливе!")
                stack.append(a / b)
                
    if len(stack) != 1:
        raise ValueError("Некоректний математичний вираз")
        
    return stack[0]


def calculate_string(expression: str):
    """Головна функція для обчислення текстового виразу."""
    try:
        tokens = tokenize(expression)
        if not tokens:
            return "Введено порожній вираз"
        
        rpn = shunting_yard(tokens)
        result = evaluate_rpn(rpn)
        
        # Перетворюємо на int, якщо результат є цілим числом
        return int(result) if result.is_integer() else result
        
    except (ValueError, ZeroDivisionError) as err:
        return f"Помилка: {err}"


def main():
    print("--- Текстовий калькулятор ---")
    expr = input("Введіть математичний вираз (наприклад, 2 + 3 * (4 - 1)): ")
    result = calculate_string(expr)
    print(f"Результат: {result}")


if __name__ == "__main__":
    main()