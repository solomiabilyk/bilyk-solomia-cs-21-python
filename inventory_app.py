import csv
import math
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox, filedialog

FIELDS = ["id", "name", "category", "quantity", "price", "location", "created_at"]
TITLES = {"id": "ID", "name": "Назва", "category": "Категорія", "quantity": "Кількість",
          "price": "Ціна", "location": "Розташування", "created_at": "Створено"}
RED, WHITE = "#ffd6d6", "white"


def validate(raw):
    """Перевіряє дані. Повертає (очищені_дані, {поле: підказка_про_помилку})."""
    d = {k: str(raw.get(k) or "").strip() for k in FIELDS}
    bad = {}
    if not d["name"]:
        bad["name"] = "Назва не може бути порожньою"
    if not d["category"]:
        bad["category"] = "Категорія не може бути порожньою"
    if d["quantity"].isdecimal():
        d["quantity"] = str(int(d["quantity"]))
    else:
        bad["quantity"] = "Кількість має бути цілим числом ≥ 0"
    try:
        price = float(d["price"].replace(",", "."))  # кому замінюємо на крапку
        if not math.isfinite(price) or price < 0:
            raise ValueError
        d["price"] = f"{price:.2f}"
    except ValueError:
        bad["price"] = "Ціна має бути числом ≥ 0 (наприклад 12.50)"
    return d, bad


class ProductStorage:
    """Сховище: тримає товари в пам'яті та вміє читати/писати CSV."""

    def __init__(self):
        self.items = {}  # {id: словник із даними товару}

    def add(self, p):
        if not p["id"]:  # порожній id -> генеруємо перший вільний номер
            n = 1
            while str(n) in self.items:
                n += 1
            p["id"] = str(n)
        if p["id"] in self.items:
            raise ValueError(f"ID «{p['id']}» вже існує")
        p["created_at"] = p["created_at"] or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.items[p["id"]] = p

    def update(self, old_id, p):
        p["id"] = p["id"] or old_id
        if p["id"] != old_id and p["id"] in self.items:
            raise ValueError(f"ID «{p['id']}» вже існує")
        p["created_at"] = self.items[old_id]["created_at"]  # дата створення не змінюється
        self.items = {(p["id"] if k == old_id else k): (p if k == old_id else v)
                      for k, v in self.items.items()}  # замінюємо запис, зберігаючи порядок

    def delete(self, pid):
        del self.items[pid]

    def load(self, path):
        old, self.items = self.items, {}  # запам'ятали старі дані на випадок помилки
        try:
            with open(path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames != FIELDS:
                    raise ValueError("Невірні заголовки. Очікується: " + ",".join(FIELDS))
                for n, row in enumerate(reader, start=2):
                    d, bad = validate(row)
                    if bad:
                        raise ValueError(f"Рядок {n}: " + "; ".join(bad.values()))
                    self.add(d)
        except Exception:
            self.items = old  # щось пішло не так — повертаємо старі дані
            raise

    def save(self, path):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(self.items.values())


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Облік товарів")
        self.geometry("1000x560")
        self.store, self.path = ProductStorage(), None
        self.sort_col, self.sort_rev = None, False
        self.vars = {k: tk.StringVar() for k in FIELDS[:-1]}  # поля форми (без created_at)
        self.status = tk.StringVar(value="Готово до роботи")
        self.search = tk.StringVar()
        self.search.trace_add("write", self.on_search)  # реагуємо на кожну введену літеру
        self.build_menu()
        self.build_ui()

    def build_menu(self):
        bar, file = tk.Menu(self), tk.Menu(self, tearoff=0)
        file.add_command(label="Відкрити...", command=self.open_file)
        file.add_command(label="Зберегти", command=self.save)
        file.add_command(label="Зберегти як...", command=self.save_as)
        bar.add_cascade(label="Файл", menu=file)
        self.config(menu=bar)

    def build_ui(self):
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w", padding=4).pack(side="bottom", fill="x")
        form = ttk.Frame(self, padding=8)
        form.pack(side="bottom", fill="x")
        top = ttk.Frame(self, padding=8)
        top.pack(side="top", fill="x")
        ttk.Label(top, text="Пошук (назва/категорія):").pack(side="left")
        ttk.Entry(top, textvariable=self.search, width=40).pack(side="left", padx=6)
        box = ttk.Frame(self)
        box.pack(fill="both", expand=True, padx=8)
        self.tree = ttk.Treeview(box, columns=FIELDS, show="headings", selectmode="browse")
        scroll = ttk.Scrollbar(box, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        for c in FIELDS:
            self.tree.heading(c, text=TITLES[c], command=lambda c=c: self.sort_by(c))
            self.tree.column(c, width=60 if c == "id" else 130)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.entries = {}
        for i, k in enumerate(FIELDS[:-1]):
            ttk.Label(form, text=TITLES[k]).grid(row=0, column=i, sticky="w", padx=3)
            e = tk.Entry(form, textvariable=self.vars[k], width=16)
            e.grid(row=1, column=i, padx=3, pady=2)
            self.entries[k] = e
        buttons = ttk.Frame(form)
        buttons.grid(row=2, column=0, columnspan=6, sticky="w", pady=6)
        for text, cmd in [("Додати", self.add_item), ("Оновити", self.update_item),
                          ("Видалити", self.delete_item), ("Очистити форму", self.clear_form)]:
            ttk.Button(buttons, text=text, command=cmd).pack(side="left", padx=3)

    def say(self, text):
        self.status.set(text)

    def refresh(self):
        q = self.search.get().strip().lower()
        rows = [p for p in self.store.items.values() if q in p["name"].lower() or q in p["category"].lower()]
        if self.sort_col:
            def key(p):
                try:
                    return (0, float(p[self.sort_col]), "")  # числа сортуємо як числа
                except ValueError:
                    return (1, 0, p[self.sort_col].lower())
            rows.sort(key=key, reverse=self.sort_rev)
        self.tree.delete(*self.tree.get_children())
        for p in rows:
            self.tree.insert("", "end", iid=p["id"], values=[p[k] for k in FIELDS])

    def on_search(self, *_):
        self.refresh()
        self.say(f"Знайдено: {len(self.tree.get_children())} з {len(self.store.items)}")

    def sort_by(self, col):
        self.sort_rev = (not self.sort_rev) if self.sort_col == col else False
        self.sort_col = col
        self.refresh()

    def on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            return
        for k, v in self.vars.items():
            v.set(self.store.items[sel[0]][k])
        for e in self.entries.values():
            e.config(bg=WHITE)

    def clear_form(self):
        for v in self.vars.values():
            v.set("")
        for e in self.entries.values():
            e.config(bg=WHITE)
        self.tree.selection_remove(*self.tree.selection())

    def read_form(self):
        d, bad = validate({k: v.get() for k, v in self.vars.items()})
        for k, e in self.entries.items():
            e.config(bg=RED if k in bad else WHITE)  # підсвічуємо помилкові поля
        if bad:
            self.say("⚠ " + "; ".join(bad.values()))
            return None
        return d

    def selected(self):
        sel = self.tree.selection()
        if not sel:
            self.say("⚠ Спочатку оберіть запис у таблиці")
            return None
        return sel[0]

    def add_item(self):
        d = self.read_form()
        if d is None:
            return
        try:
            self.store.add(d)
        except ValueError as e:
            return self.say("⚠ " + str(e))
        self.refresh()
        self.clear_form()
        self.say(f"Додано: {d['name']}")

    def update_item(self):
        sid = self.selected()
        d = self.read_form() if sid else None
        if d is None:
            return
        try:
            self.store.update(sid, d)
        except ValueError as e:
            return self.say("⚠ " + str(e))
        self.refresh()
        if self.tree.exists(d["id"]):
            self.tree.selection_set(d["id"])
        self.say(f"Оновлено: {d['name']}")

    def delete_item(self):
        sid = self.selected()
        if sid is None:
            return
        name = self.store.items[sid]["name"]
        if messagebox.askyesno("Підтвердження", f"Видалити «{name}»?"):
            self.store.delete(sid)
            self.refresh()
            self.clear_form()
            self.say(f"Видалено: {name}")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV файли", "*.csv")])
        if not path:
            return
        try:
            self.store.load(path)
        except (OSError, ValueError, csv.Error) as e:
            return messagebox.showerror("Помилка відкриття", str(e))
        self.path = path
        self.clear_form()
        self.refresh()
        self.say(f"Відкрито {path}: {len(self.store.items)} записів")

    def save(self):
        if not self.path:
            return self.save_as()
        try:
            self.store.save(self.path)
        except OSError as e:
            return messagebox.showerror("Помилка збереження", str(e))
        self.say(f"Збережено в {self.path}")

    def save_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV файли", "*.csv")])
        if path:
            self.path = path
            self.save()


if __name__ == "__main__":
    App().mainloop()