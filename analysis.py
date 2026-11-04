import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse

def main():
    # 8. Додаємо можливість передавати CSV як аргумент через argparse
    parser = argparse.ArgumentParser(description="Аналіз даних поставок")
    parser.add_argument('--file', type=str, default='supplies.csv', help='Шлях до CSV файлу з поставками')
    args = parser.parse_args()

    # 1. Завантаження даних з CSV за допомогою pandas
    df = pd.read_csv(args.file)

    prices = df['price_per_unit'].to_numpy()
    quantities = df['quantity'].to_numpy()

    # 2. Обчислення за допомогою NumPy:
    mean_price = np.mean(prices)
    median_quantity = np.median(quantities)
    std_price = np.std(prices, ddof=1)

    print(f"Середня ціна всіх препаратів: {mean_price:.2f}")
    print(f"Медіана кількості (quantity): {median_quantity}")
    print(f"Стандартне відхилення ціни (price_per_unit): {std_price:.2f}")

    # 3. Обчислення за допомогою Pandas:
    # - Додаємо обчислене поле total_price (також використовується для прибутку)
    df['total_price'] = df['quantity'] * df['price_per_unit']
    
    # - Постачальник з найбільшим загальним прибутком
    supplier_profit = df.groupby('supplier')['total_price'].sum()
    top_supplier = supplier_profit.idxmax()
    max_profit = supplier_profit.max()
    print(f"Постачальник з найбільшим прибутком: {top_supplier} ({max_profit:.2f})")

    # - Сумарна кількість препаратів за категоріями
    category_qty = df.groupby('category')['quantity'].sum()
    print("\nСумарна кількість препаратів за категоріями:\n", category_qty)

    # - Фільтрація записів, де quantity < 100, та збереження у low_supply.csv
    low_supply_df = df[df['quantity'] < 100]
    low_supply_df.to_csv('low_supply.csv', index=False)
    print("Файл з дефіцитними поставками збережено: low_supply.csv")

    # 5. Сортування даних за total_price у порядку спадання й виведення перших трьох рядків
    sorted_df = df.sort_values(by='total_price', ascending=False)
    print("\nПерші три рядки (найвищий total_price):")
    print(sorted_df.head(3))

    # 6. Створення простого звіту у форматі .txt (report.txt)
    report_content = f"""Звіт щодо аналізу поставок:
- Середня ціна препаратів: {mean_price:.2f}
- Медіана кількості (quantity): {median_quantity}
- Стандартне відхилення ціни (price_per_unit): {std_price:.2f}
- Постачальник з найбільшим загальним прибутком: {top_supplier} ({max_profit:.2f})
- Назва створеного файлу з дефіцитними поставками: low_supply.csv
"""
    with open('report.txt', 'w', encoding='utf-8') as f:
        f.write(report_content)
    print("Звіт успішно записано у report.txt")

    # 7. Побудова графіка розподілу кількості препаратів за категоріями через matplotlib
    plt.figure(figsize=(8, 6))
    category_qty.plot(kind='bar', color='cornflowerblue', edgecolor='black')
    plt.title('Розподіл кількості препаратів за категоріями')
    plt.xlabel('Категорія')
    plt.ylabel('Сумарна кількість')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('category_distribution.png')
    plt.close()
    print("Графік збережено у файлі category_distribution.png")

if __name__ == '__main__':
    main()