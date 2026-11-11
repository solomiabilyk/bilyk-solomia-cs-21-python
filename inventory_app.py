import csv
import math
import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import ttk, messagebox, filedialog

FIELDS = ["id", "name", "category", "quantity", "price", "location", "created_at"]
# тут запам'ятовується шлях до останнього файлу (лежить поруч зі скриптом)
LAST_FILE = Path(__file__).with_name("last_file.txt")
LABELS = ["ID", "Назва", "Категорія", "Кількість", "Ціна", "Склад/полиця", "Створено"]


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def next_id(ids):
    """Наступний вільний числовий id."""
    return str(max([int(i) for i in ids if i.isascii() and i.isdigit()] + [0]) + 1)


def sort_key(value):
    """Числа сортуються як числа, решта — як текст без урахування регістру."""
    try:
        return (0, float(value), "")
    except ValueError:
        return (1, 0.0, value.lower())


def validate(raw):
    item = {f: str(raw.get(f) or "").strip() for f in FIELDS}
    errors = {}
    for f in ("name", "category"):
        if not item[f]:
            errors[f] = f"поле «{LABELS[FIELDS.index(f)]}» порожнє"
    if item["quantity"].isascii() and item["quantity"].isdigit():
        item["quantity"] = str(int(item["quantity"]))
    else:
        errors["quantity"] = "кількість — ціле число ≥ 0"
    try:
        price = float(item["price"].replace(",", "."))
        if not math.isfinite(price) or price < 0:
            raise ValueError
        item["price"] = f"{price:.2f}"
    except ValueError:
        errors["price"] = "ціна — число ≥ 0"
    return item, errors


class CsvStorage:
    """Уся робота з файлом тут — вікно викликає лише load() і save()."""
    filetypes = [("CSV", "*.csv")]

    def load(self, path):
        with open(path, encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if not set(FIELDS[:-1]) <= set(reader.fieldnames or []):
                raise ValueError("Неправильні заголовки. Потрібно: " + ",".join(FIELDS))
            return list(reader)

    def save(self, path, items):
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(items)


class App:
    def __init__(self, root, storage):
        self.root, self.storage = root, storage
        self.items, self.path, self.selected = {}, None, None
        self.sort_col, self.sort_desc, self.dirty = None, False, False
        root.title("Облік товарів")
        root.geometry("1100x520")
        style = ttk.Style()
        style.theme_use("clam")  # у цій темі підсвічування полів працює скрізь
        style.configure("Error.TEntry", fieldbackground="#ffc9c9")
        menu, file_menu = tk.Menu(root), tk.Menu(root, tearoff=0)
        for label, cmd in [("Відкрити...", self.open), ("Зберегти (Ctrl+S)", self.save),
                           ("Зберегти як...", lambda: self.save(True))]:
            file_menu.add_command(label=label, command=cmd)
        menu.add_cascade(label="Файл", menu=file_menu)
        root.config(menu=menu)
        root.bind("<Control-s>", lambda e: self.save())
        root.protocol("WM_DELETE_WINDOW", lambda: root.destroy() if self.confirm_discard() else None)

        self.search = tk.StringVar()
        self.search.trace_add("write", lambda *a: self.refresh())
        ttk.Label(root, text="Пошук (назва/категорія):").grid(row=0, column=0, padx=5)
        ttk.Entry(root, textvariable=self.search).grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        box = ttk.Frame(root)
        box.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5)
        self.tree = ttk.Treeview(box, columns=FIELDS, show="headings", selectmode="browse")
        scroll = ttk.Scrollbar(box, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        for f, label in zip(FIELDS, LABELS):
            self.tree.heading(f, text=label, command=lambda f=f: self.sort_by(f))
            self.tree.column(f, width=60 if f == "id" else 110)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        form = ttk.Frame(root)
        form.grid(row=1, column=2, sticky="n", padx=8)
        self.vars, self.entries = {}, {}
        for i, (f, label) in enumerate(zip(FIELDS[:-1], LABELS)):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w")
            self.vars[f] = tk.StringVar()
            self.entries[f] = ttk.Entry(form, textvariable=self.vars[f])
            self.entries[f].grid(row=i, column=1, pady=2)
        buttons = [("Додати", self.save_item), ("Оновити", lambda: self.save_item(True)),
                   ("Видалити", self.delete), ("Очистити форму", self.clear)]
        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(form, text=text, command=cmd).grid(row=10 + i, column=0, columnspan=2, sticky="ew", pady=1)
        self.status = ttk.Label(root, text="Готово", relief="sunken", anchor="w")
        self.status.grid(row=2, column=0, columnspan=3, sticky="ew")
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)
        self.restore_last()

    def say(self, text):
        self.status.config(text=text)

    def confirm_discard(self):
        return not self.dirty or messagebox.askyesno("Незбережені зміни", "Є незбережені зміни. Продовжити без збереження?")

    def refresh(self, message=None):
        q = self.search.get().strip().lower()
        rows = [it for it in self.items.values() if q in it["name"].lower() or q in it["category"].lower()]
        if self.sort_col:
            rows.sort(key=lambda it: sort_key(it[self.sort_col]), reverse=self.sort_desc)
        self.tree.delete(*self.tree.get_children())
        for it in rows:
            self.tree.insert("", "end", iid=it["id"], values=[it[f] for f in FIELDS])
        for f, label in zip(FIELDS, LABELS):  # стрілка біля колонки сортування
            arrow = (" ▼" if self.sort_desc else " ▲") if f == self.sort_col else ""
            self.tree.heading(f, text=label + arrow)
        if self.selected and self.tree.exists(self.selected):
            self.tree.selection_set(self.selected)
        else:
            self.selected = None
        self.say(message or f"Показано {len(rows)} з {len(self.items)}")

    def sort_by(self, col):
        self.sort_desc = (not self.sort_desc) if self.sort_col == col else False
        self.sort_col = col
        self.refresh()

    def on_select(self, event):
        sel = self.tree.selection()
        if sel and sel[0] != self.selected:
            self.selected = sel[0]
            for f in self.vars:
                self.vars[f].set(self.items[sel[0]][f])
                self.entries[f].configure(style="TEntry")

    def clear(self):
        self.selected = None
        self.tree.selection_remove(self.tree.selection())
        for f in self.vars:
            self.vars[f].set("")
            self.entries[f].configure(style="TEntry")

    def save_item(self, update=False):
        if update and not self.selected:
            return self.say("Оберіть товар у таблиці")
        old_id = self.selected if update else None
        raw = {f: v.get() for f, v in self.vars.items()}
        if update and not raw["id"].strip():
            raw["id"] = old_id  # порожній id при оновленні — залишаємо старий
        item, errors = validate(raw)
        item["id"] = item["id"] or next_id(self.items)
        if item["id"] in self.items and item["id"] != old_id:
            errors["id"] = "такий ID вже існує"
        for f, entry in self.entries.items():  # підсвічуємо некоректні поля
            entry.configure(style="Error.TEntry" if f in errors else "TEntry")
        if errors:
            return self.say("Помилка: " + "; ".join(errors.values()))
        if update:  # замінюємо запис на тому ж місці
            item["created_at"] = self.items[old_id]["created_at"]
            self.items = {(item["id"] if k == old_id else k): (item if k == old_id else v)
                          for k, v in self.items.items()}
        else:
            item["created_at"] = now()
            self.items[item["id"]] = item
        self.dirty = True
        self.clear()
        self.refresh(("Оновлено: " if update else "Додано: ") + item["name"])

    def delete(self):
        if not self.selected:
            return self.say("Оберіть товар у таблиці")
        name = self.items[self.selected]["name"]
        if messagebox.askyesno("Видалення", f"Видалити «{name}»?"):
            del self.items[self.selected]
            self.dirty = True
            self.clear()
            self.refresh(f"Видалено: {name}")

    def remember(self, path):
        try:
            LAST_FILE.write_text(path, encoding="utf-8")
        except OSError:
            pass  # не вдалося запам'ятати — не страшно, програма працює далі

    def restore_last(self):
        """При запуску автоматично відкриває файл, з яким працювали минулого разу."""
        try:
            path = LAST_FILE.read_text(encoding="utf-8").strip()
        except OSError:
            return
        if path and Path(path).is_file():
            self.load_path(path, quiet=True)

    def open(self):
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(filetypes=self.storage.filetypes)
        if path:
            self.load_path(path)

    def load_path(self, path, quiet=False):
        try:
            loaded, rows = {}, self.storage.load(path)
            taken = [str(r.get("id") or "").strip() for r in rows]  # id, які вже є у файлі
            for n, row in enumerate(rows, start=2):
                item, errors = validate(row)
                if not item["id"]:  # порожній id — видаємо вільний, що не збігається з жодним у файлі
                    item["id"] = next_id(list(loaded) + taken)
                    taken.append(item["id"])
                if errors or item["id"] in loaded:
                    raise ValueError(f"Рядок {n}: " + ("; ".join(errors.values()) or "ID повторюється"))
                item["created_at"] = item["created_at"] or now()
                loaded[item["id"]] = item
        except (OSError, ValueError, csv.Error) as e:
            if quiet:  # при автозапуску без вікон з помилками, лише рядок стану
                return self.say(f"Не вдалося відкрити останній файл: {e}")
            return messagebox.showerror("Помилка відкриття", str(e))
        self.items, self.path, self.dirty = loaded, path, False  # повна заміна даних
        self.remember(path)
        self.clear()
        self.refresh(f"Завантажено {len(loaded)} товарів з {path}")

    def save(self, ask_path=False):
        """Зберігає дані; повертає True, якщо збережено, і False, якщо ні."""
        path = self.path if self.path and not ask_path else \
            filedialog.asksaveasfilename(defaultextension=".csv", filetypes=self.storage.filetypes)
        if not path:
            return False
        try:
            self.storage.save(path, self.items.values())
        except OSError as e:
            messagebox.showerror("Помилка збереження", str(e))
            return False
        self.path, self.dirty = path, False  # запам'ятали файл і зняли позначку «є зміни»
        self.remember(path)  # записуємо шлях у last_file.txt для автозавантаження
        self.say(f"Збережено у {path}")
        return True


if __name__ == "__main__":
    root = tk.Tk()
    App(root, CsvStorage())
    root.mainloop()
