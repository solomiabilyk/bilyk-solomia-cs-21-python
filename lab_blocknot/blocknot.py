from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

BROKEN_VALUE_COEFFICIENT: float = 0.2
USED_VALUE_COEFFICIENT: float = 0.7
NEW_VALUE_COEFFICIENT: float = 1.0

_KNOWN_INVENTORY_NAMES: set[str] = set()


class Condition(str, Enum):
    NEW = "новий"
    USED = "уживаний"
    BROKEN = "зламаний"


CONDITION_COEFFICIENTS: dict[Condition, float] = {
    Condition.NEW: NEW_VALUE_COEFFICIENT,
    Condition.USED: USED_VALUE_COEFFICIENT,
    Condition.BROKEN: BROKEN_VALUE_COEFFICIENT,
}


@dataclass
class Item:
    name: str
    category: str
    quantity: int
    value: float
    condition: Condition
    location: str
    added_at: datetime = field(default_factory=datetime.now, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.condition, Condition):
            self.condition = Condition(self.condition)

    def total_value(self) -> float:
        coefficient = CONDITION_COEFFICIENTS.get(self.condition, NEW_VALUE_COEFFICIENT)
        return self.quantity * self.value * coefficient

    def __str__(self) -> str:
        condition_text = (
            self.condition.value if isinstance(self.condition, Condition) else str(self.condition)
        )
        return (
            f"[{self.category}] {self.name} ({self.quantity} шт.) - "
            f"{self.value} грн/шт, стан: {condition_text}"
        )


@dataclass
class Inventory:
    name: str = "основний"
    items: list[Item] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.name in _KNOWN_INVENTORY_NAMES:
            raise ValueError(f"Склад з назвою '{self.name}' уже існує")
        _KNOWN_INVENTORY_NAMES.add(self.name)

    def add_item(self, item: Item) -> None:
        self.items.append(item)

    def remove_item(self, name: str) -> bool:
        for index, item in enumerate(self.items):
            if item.name == name:
                del self.items[index]
                return True
        return False

    def find_by_category(self, category: str) -> list[Item]:
        return [item for item in self.items if item.category == category]

    def total_inventory_value(self) -> float:
        return sum(item.total_value() for item in self.items)

    def filter_items(self, **criteria: Any) -> list[Item]:
        result: list[Item] = []
        for item in self.items:
            matched = True
            for field_name, expected in criteria.items():
                if not hasattr(item, field_name):
                    raise AttributeError(f"Поле '{field_name}' відсутнє у Item")
                actual = getattr(item, field_name)
                if field_name == "condition" and not isinstance(expected, Condition):
                    expected = Condition(expected)
                if actual != expected:
                    matched = False
                    break
            if matched:
                result.append(item)
        return result

    def sorted_items(self, order: bool = True) -> list[Item]:
        if not order:
            return list(self.items)
        return sorted(
            self.items,
            key=lambda item: (
                item.category,
                item.value,
                item.name,
                item.location,
                item.quantity,
                item.condition.value,
            ),
        )

    def save_to_csv(self, filepath: str | Path) -> None:
        path = Path(filepath)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, delimiter=";", lineterminator="\n")
            for item in self.items:
                cond_val = (
                    item.condition.value
                    if isinstance(item.condition, Condition)
                    else str(item.condition)
                )
                writer.writerow(
                    [item.name, item.category, item.quantity, item.value, cond_val, item.location]
                )

    def export_summary(self) -> dict[str, int]:
        summary: dict[str, int] = {}
        for item in self.items:
            summary[item.category] = summary.get(item.category, 0) + item.quantity
        return summary


def load(filepath: str | Path, inventory_name: str | None = None) -> Inventory:
    resolved_name = inventory_name or f"склад_{id(object())}"
    inventory = Inventory(name=resolved_name)
    path = Path(filepath)
    with path.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split(";")
            inventory.add_item(
                Item(
                    name=parts[0],
                    category=parts[1],
                    quantity=int(parts[2]),
                    value=float(parts[3]),
                    condition=Condition(parts[4]),
                    location=parts[5],
                )
            )
    return inventory


def load_from_csv(filepath: str | Path, inventory_name: str | None = None) -> Inventory:
    return load(filepath, inventory_name=inventory_name)


def zvit(filepath: str | Path) -> None:
    inventory = load(filepath)
    total_all = round(inventory.total_inventory_value(), 2)
    print("Барахла:", len(inventory.items))
    for item in sorted(inventory.items, key=lambda entry: entry.location):
        item_total = round(item.total_value(), 2)
        print(item.location, "|", item.name, "|", item.quantity, "шт |", item_total)
    print("Разом:", total_all)


if __name__ == "__main__":
    zvit("barakhlo.csv")