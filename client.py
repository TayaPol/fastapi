"""
Простой клиент для управления торговыми автоматами
Запуск: python client.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
import requests


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Вендинг")
        self.root.geometry("800x500")
        self.api_url = "http://localhost:8000"
        self.setup_ui()
        self.load_machines()

    def setup_ui(self):
        """Создаёт интерфейс"""
        # Кнопки
        frame = ttk.Frame(self.root)
        frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(frame, text="Обновить", command=self.load_machines).pack(side="left", padx=5)
        ttk.Button(frame, text="Добавить ТА", command=self.add_machine).pack(side="left", padx=5)

        # Таблица
        columns = ("id", "name", "model", "status", "location")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        # Заголовки
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Название")
        self.tree.heading("model", text="Модель")
        self.tree.heading("status", text="Статус")
        self.tree.heading("location", text="Расположение")

        # Ширина колонок
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=200)
        self.tree.column("model", width=150)
        self.tree.column("status", width=120)
        self.tree.column("location", width=350)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Двойной клик для изменения статуса
        self.tree.bind("<Double-1>", self.change_status)

    def load_machines(self):
        """Загружает список ТА с сервера"""
        try:
            response = requests.get(f"{self.api_url}/machines")
            machines = response.json()

            # Очистить таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Заполнить данными
            for m in machines:
                self.tree.insert("", "end", values=(
                    m["id"],
                    m["name"],
                    m["model"],
                    m["status"],
                    m["location"]
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")

    def add_machine(self):
        """Форма добавления нового ТА"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить ТА")
        dialog.geometry("400x350")

        # Поля ввода
        fields = [
            ("serial_number", "Серийный номер:", "SN123"),
            ("inventory_number", "Инвентарный номер:", "INV456"),
            ("name", "Название:", "Автомат #1"),
            ("model", "Модель:", "CoffeeMaster 2000"),
            ("location", "Расположение:", "ТЦ Атриум"),
            ("address", "Адрес:", "ул. Ленина, 10")
        ]

        entries = {}
        for i, (name, label, default) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=5)
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, default)
            entries[name] = entry

        # Кнопка сохранения
        def save():
            data = {name: entry.get() for name, entry in entries.items()}

            # Проверка обязательных полей
            if not data["serial_number"] or not data["inventory_number"] or not data["name"]:
                messagebox.showwarning("Внимание", "Заполните обязательные поля!")
                return

            try:
                response = requests.post(f"{self.api_url}/machines", json=data)
                if response.status_code == 200:
                    messagebox.showinfo("Успех", "ТА добавлен!")
                    dialog.destroy()
                    self.load_machines()
                else:
                    messagebox.showerror("Ошибка", response.json().get("detail", "Неизвестная ошибка"))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сети:\n{str(e)}")

        ttk.Button(dialog, text="Сохранить", command=save, width=25).grid(
            row=len(fields), column=0, columnspan=2, pady=20
        )

    def change_status(self, event):
        """Изменяет статус ТА по двойному клику"""
        item = self.tree.selection()
        if not item:
            return

        machine_id = self.tree.item(item[0])["values"][0]
        current_status = self.tree.item(item[0])["values"][3]

        # Новый статус (циклически)
        statuses = ["Работает", "Вышел из строя", "В ремонте"]
        current_idx = statuses.index(current_status) if current_status in statuses else 0
        new_status = statuses[(current_idx + 1) % len(statuses)]

        try:
            response = requests.put(
                f"{self.api_url}/machines/{machine_id}/status",
                params={"new_status": new_status}
            )
            if response.status_code == 200:
                self.load_machines()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()