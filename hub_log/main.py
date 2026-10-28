from collections import Counter
import functools
import re

VALID_TYPES = {"GATE", "CARGO", "ACCESS", "ALARM", "SENSOR", "CALL", "SYSTEM"}
TIME_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")


def log_generator(file_path):
  """Генератор: читає файл рядок за рядком, не завантажуючи у пам'ять."""
  with open(file_path, "r", encoding="utf-8") as f:
    for line in f:
      stripped = line.strip()
      if stripped:
        yield stripped


def validate_log_line(line):
  """Перевіряє валідність рядка логу."""
  parts = line.split("|")
  if len(parts) < 2:
    return False

  time_str, event_type = parts[0], parts[1]

  if not TIME_REGEX.match(time_str):
    return False
  if event_type not in VALID_TYPES:
    return False

  for part in parts[2:]:
    if "=" not in part:
      return False

  return True


def filter_valid_logs(func):
  """Перший декоратор: фільтрує валідні рядки та рахує биті."""

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    corrupted_count = 0
    valid_lines = []

    for line in func(*args, **kwargs):
      if validate_log_line(line):
        valid_lines.append(line)
      else:
        corrupted_count += 1

    # Повертаємо кортеж: список валідних рядків та кількість битих
    return valid_lines, corrupted_count

  return wrapper


def report_statistics(func):
  """Другий декоратор: рахує події за типами та друкує звіт."""

  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    # Отримуємо результати від попередньої обгортки
    valid_lines, corrupted_count = func(*args, **kwargs)
    event_counts = Counter()

    for line in valid_lines:
      parts = line.split("|")
      event_type = parts[1]
      event_counts[event_type] += 1

    # Виведення звіту
    print("=" * 40)
    print("           ЗВІТ СИСТЕМИ ЛОГІВ")
    print("=" * 40)
    print(f"{'Тип події':<15} | {'Кількість':<10}")
    print("-" * 30)

    total_valid = 0
    for event_type in sorted(VALID_TYPES):
      count = event_counts[event_type]
      total_valid += count
      print(f"{event_type:<15} | {count:<10}")

    print("-" * 30)
    print(f"Всього валідних: {total_valid}")
    print(f"Битих рядків:   {corrupted_count}")
    print("=" * 40)

    return event_counts, corrupted_count

  return wrapper


# Порядок застосування: спочатку фільтрація, потім звіт
@report_statistics
@filter_valid_logs
def process_logs(file_path):
  return log_generator(file_path)


if __name__ == "__main__":
  print("--- Перший виклик процесингу ---")
  process_logs("hub_log.txt")

  print("\n--- Повторний виклик (перевірка рахунку з нуля) ---")
  process_logs("hub_log.txt")