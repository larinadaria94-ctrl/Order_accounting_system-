from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Tuple

from .db import Database
from .utils import merge_sort, now_date_str
from .models import Client, Product
from . import analysis as anl



class App(ttk.Frame):
    def __init__(self, master, db: Database):
        super().__init__(master)
        self.db = db
        self.pack(fill="both", expand=True)
        self._build()

    def _build(self):
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True)
        self._clients_tab(nb)
        self._products_tab(nb)
        self._orders_tab(nb)
        self._analysis_tab(nb)
        self._admin_tab(nb)

    def _clients_tab(self, nb):
        f = ttk.Frame(nb); nb.add(f, text="Клиенты")

        frm = ttk.LabelFrame(f, text="Добавить/Изменить клиента")
        frm.pack(fill="x", padx=6, pady=6)

        self.c_name = ttk.Entry(frm); self.c_email = ttk.Entry(frm)
        self.c_phone = ttk.Entry(frm); self.c_addr = ttk.Entry(frm)
        for i, (lbl, w) in enumerate((
            ("Имя:", self.c_name),
            ("Email:", self.c_email),
            ("Телефон:", self.c_phone),
            ("Адрес:", self.c_addr),
        )):
            ttk.Label(frm, text=lbl).grid(row=i, column=0, padx=4, pady=4, sticky="e")
            w.grid(row=i, column=1, padx=4, pady=4, sticky="we")
        frm.columnconfigure(1, weight=1)
        ttk.Button(frm, text="Сохранить", command=self._save_client).grid(row=4, column=0, columnspan=2, pady=6)

        search_fr = ttk.Frame(f); search_fr.pack(fill="x", padx=6, pady=2)
        ttk.Label(search_fr, text="Поиск:").pack(side="left")
        self.c_search = ttk.Entry(search_fr); self.c_search.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(search_fr, text="Найти", command=self._find_clients).pack(side="left")

        self.c_search_info = ttk.Label(f, text="", foreground="#666")
        self.c_search_info.pack(fill="x", padx=6, pady=(0, 6))

        self.clients_tv = ttk.Treeview(f, columns=("id","name","email","phone","address"), show="headings", height=8)
        for c in ("id","name","email","phone","address"):
            self.clients_tv.heading(c, text=c.upper())
        self.clients_tv.pack(fill="both", expand=True, padx=6, pady=6)

        self._reload_clients()

        btns = ttk.Frame(f); btns.pack(fill="x", padx=6, pady=4)
        ttk.Button(btns, text="Удалить выбранного клиента", command=self._delete_client).pack(side="left")


    def _save_client(self):
        try:
            name = self.c_name.get().strip()
            email = self.c_email.get().strip()
            phone = self.c_phone.get().strip()
            addr = self.c_addr.get().strip()
            if not name:
                raise ValueError("Имя обязательно")

            c = Client(name, email, phone, addr)

            self.db.add_client(c.name, c.email, c.phone, c.address)
            self._reload_clients()
            messagebox.showinfo("OK", "Клиент сохранён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete_client(self):
        try:
            sel = self.clients_tv.selection()
            if not sel:
                raise ValueError("Не выбран клиент")
            values = self.clients_tv.item(sel[0])["values"]
            cid = int(values[0])
            if not messagebox.askyesno("Подтвердите", f"Удалить клиента ID={cid}? Его заказы удалятся."):
                return
            self.db.delete_client(cid)
            self._reload_clients()
            self._reload_orders()
            self._refresh_order_combos()
            messagebox.showinfo("OK", "Клиент удалён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


    def _reload_clients(self, rows=None):
        for i in self.clients_tv.get_children():
            self.clients_tv.delete(i)
        rows = rows or self.db.list_clients()
        for r in rows:
            self.clients_tv.insert("", "end", values=(r["id"], r["name"], r["email"], r["phone"], r["address"]))

    def _find_clients(self, q=None, event=None):
        query = q.strip() if isinstance(q, str) else self.c_search.get().strip()

        if not query:
            rows = self.db.list_clients()
            self._reload_clients(rows)
            if hasattr(self, "c_search_info"):
                self.c_search_info.config(text="")
            return

        if query.isdigit():
            rows = self.db.get_client_by_id(int(query))
        else:
            rows = self.db.find_clients(query)

        if not rows:
            self._reload_clients(self.db.list_clients())
            if hasattr(self, "c_search_info"):
                self.c_search_info.config(text=f"Ничего не найдено по «{query}». Показаны все клиенты.")
            return

        self._reload_clients(rows)
        if hasattr(self, "c_search_info"):
            self.c_search_info.config(text=f"Найдено: {len(rows)}")

    def _products_tab(self, nb):
        f = ttk.Frame(nb); nb.add(f, text="Товары")
        frm = ttk.LabelFrame(f, text="Добавить товар"); frm.pack(fill="x", padx=6, pady=6)
        self.p_name = ttk.Entry(frm); self.p_price = ttk.Entry(frm)
        ttk.Label(frm, text="Название:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.p_name.grid(row=0, column=1, padx=4, pady=4, sticky="we")
        ttk.Label(frm, text="Цена:").grid(row=1, column=0, padx=4, pady=4, sticky="e")
        self.p_price.grid(row=1, column=1, padx=4, pady=4, sticky="we")
        frm.columnconfigure(1, weight=1)
        ttk.Button(frm, text="Сохранить", command=self._save_product).grid(row=2, column=0, columnspan=2, pady=6)

        self.products_tv = ttk.Treeview(f, columns=("id","name","price"), show="headings", height=10)
        for c in ("id","name","price"):
            self.products_tv.heading(c, text=c.upper())
        self.products_tv.pack(fill="both", expand=True, padx=6, pady=6)
        self._reload_products()

        btns = ttk.Frame(f); btns.pack(fill="x", padx=6, pady=4)
        ttk.Button(btns, text="Удалить выбранный товар", command=self._delete_product).pack(side="left")

    def _delete_product(self):
        try:
            sel = self.products_tv.selection()
            if not sel:
                raise ValueError("Не выбран товар")
            values = self.products_tv.item(sel[0])["values"]
            pid = int(values[0])
            if not messagebox.askyesno("Подтвердите", f"Удалить товар ID={pid}?"):
                return
            self.db.delete_product(pid)
            self._reload_products()
            self._refresh_order_combos()
            messagebox.showinfo("OK", "Товар удалён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


    def _save_product(self):
        try:
            name = self.p_name.get().strip()
            if not name:
                raise ValueError("Название обязательно")

            raw = self.p_price.get().strip()
            try:
                price = float(raw)
            except ValueError:
                raise ValueError("Цена должна быть числом")

            prod = Product(name, price)

            self.db.add_product(prod.name, prod.price)
            self._reload_products()
            self._refresh_order_combos()
            messagebox.showinfo("OK", "Товар сохранён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _refresh_order_combos(self):
        if hasattr(self, "o_client"):
            self.o_client["values"] = [f'{r["id"]}: {r["name"]}' for r in self.db.list_clients()]
        if hasattr(self, "o_product"):
            self.o_product["values"] = [f'{r["id"]}: {r["name"]} — {r["price"]} руб.' for r in self.db.list_products()]


    def _reload_products(self):
        for i in self.products_tv.get_children():
            self.products_tv.delete(i)
        for r in self.db.list_products():
            self.products_tv.insert("", "end", values=(r["id"], r["name"], r["price"]))

    def _orders_tab(self, nb):
        f = ttk.Frame(nb); nb.add(f, text="Заказы")

        frm = ttk.LabelFrame(f, text="Создать заказ"); frm.pack(fill="x", padx=6, pady=6)
        ttk.Label(frm, text="Клиент:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.o_client = ttk.Combobox(frm, values=[f'{r["id"]}: {r["name"]}' for r in self.db.list_clients()], state="readonly")
        self.o_client.grid(row=0, column=1, sticky="we", padx=4, pady=4)

        ttk.Label(frm, text="Товар:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.o_product = ttk.Combobox(frm, values=[f'{r["id"]}: {r["name"]} — {r["price"]} руб.' for r in self.db.list_products()], state="readonly")
        self.o_product.grid(row=1, column=1, sticky="we", padx=4, pady=4)
        ttk.Label(frm, text="Кол-во:").grid(row=1, column=2, sticky="e")
        self.o_qty = ttk.Spinbox(frm, from_=1, to=100, width=5); self.o_qty.grid(row=1, column=3, padx=4, pady=4)

        self.order_items: List[Tuple[int,int]] = []
        ttk.Button(frm, text="Добавить в заказ", command=self._add_to_order).grid(row=1, column=4, padx=6)
        ttk.Button(frm, text="Создать заказ", command=self._create_order).grid(row=0, column=4, padx=6)

        self.items_tv = ttk.Treeview(frm, columns=("pid","name","price","qty"), show="headings", height=4)
        for c in ("pid","name","price","qty"):
            self.items_tv.heading(c, text=c.upper())
        self.items_tv.grid(row=2, column=0, columnspan=5, sticky="nsew", padx=4, pady=6)
        frm.columnconfigure(1, weight=1); frm.rowconfigure(2, weight=1)

        sort_fr = ttk.Frame(f); sort_fr.pack(fill="x", padx=6)
        ttk.Label(sort_fr, text="Сортировать заказы по:").pack(side="left")
        self.sort_key = ttk.Combobox(sort_fr, values=["date", "total"], state="readonly"); self.sort_key.set("date")
        self.sort_key.pack(side="left", padx=4)
        ttk.Button(sort_fr, text="Применить", command=self._sort_orders).pack(side="left")

        self.orders_tv = ttk.Treeview(f, columns=("id","client","date","total","total_qty"), show="headings", height=10)
        for c in ("id","client","date","total","total_qty"):
            self.orders_tv.heading(c, text=c.upper())
        self.orders_tv.pack(fill="both", expand=True, padx=6, pady=6)
        self._reload_orders()

        btns = ttk.Frame(f); btns.pack(fill="x", padx=6, pady=4)
        ttk.Button(btns, text="Удалить выбранный заказ", command=self._delete_order).pack(side="left")

    def _delete_order(self):
        try:
            sel = self.orders_tv.selection()
            if not sel:
                raise ValueError("Не выбран заказ")
            values = self.orders_tv.item(sel[0])["values"]
            oid = int(values[0])
            if not messagebox.askyesno("Подтвердите", f"Удалить заказ ID={oid}?"):
                return
            self.db.delete_order(oid)
            self._reload_orders()
            messagebox.showinfo("OK", "Заказ удалён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


    def _add_to_order(self):
        if not self.o_product.get():
            return
        pid = int(self.o_product.get().split(":")[0])
        qty = int(self.o_qty.get())
        prod = [r for r in self.db.list_products() if r["id"] == pid][0]
        self.order_items.append((pid, qty))
        self.items_tv.insert("", "end", values=(pid, prod["name"], prod["price"], qty))

    def _create_order(self):
        try:
            if not self.o_client.get():
                raise ValueError("Выберите клиента")
            if not self.order_items:
                raise ValueError("Добавьте позиции")
            client_id = int(self.o_client.get().split(":")[0])
            self.db.create_order(client_id, now_date_str(), self.order_items)
            self.order_items.clear()
            for i in self.items_tv.get_children():
                self.items_tv.delete(i)
            self._reload_orders()
            messagebox.showinfo("OK", "Заказ создан")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _reload_orders(self, rows=None):
        for i in self.orders_tv.get_children():
            self.orders_tv.delete(i)

        if rows is None:
            rows = [dict(r) for r in self.db.list_orders()]

        for r in rows:
            try:
                total = round(float(r["total"]), 2)
            except (TypeError, ValueError):
                total = r["total"]
            self.orders_tv.insert(
                "", "end",
                values=(r["id"], r["client"], r["date"], total, r["total_qty"])
            )

    def _sort_orders(self):
        rows = []
        for iid in self.orders_tv.get_children():
            v = self.orders_tv.item(iid)["values"]
            rows.append({
                "id": int(v[0]),
                "client": str(v[1]),
                "date": str(v[2]),
                "total": float(v[3]),
                "total_qty": int(v[4]),
            })

        key = self.sort_key.get()
        if key == "total":
            rows_sorted = merge_sort(rows, key=lambda r: r["total"], reverse=True)
        else:
            rows_sorted = merge_sort(rows, key=lambda r: r["date"])

        self._reload_orders(rows_sorted)

    def _analysis_tab(self, nb):
        f = ttk.Frame(nb); nb.add(f, text="Анализ и Визуализация")
        ttk.Button(f, text="Топ-5 клиентов по кол-ву заказов", command=lambda: anl.plot_top5_clients(self.db.conn)).pack(padx=6, pady=6)
        ttk.Button(f, text="Динамика заказов по датам", command=lambda: anl.plot_orders_timeline(self.db.conn)).pack(padx=6, pady=6)
        ttk.Button(f, text="Граф связей клиентов (города)", command=lambda: anl.client_graph_by_city(self.db.conn)).pack(padx=6, pady=6)

    def _admin_tab(self, nb):
        f = ttk.Frame(nb);
        nb.add(f, text="Администрирование")

        ttk.Button(f, text="Экспорт в JSON", command=self._export_json) \
            .grid(row=0, column=0, padx=6, pady=6, sticky="w")
        ttk.Button(f, text="Импорт из JSON", command=self._import_json) \
            .grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ttk.Button(f, text="Экспорт CSV (CP1251 для Excel)", command=lambda: self.db.export_csv(encoding="cp1251")) \
            .grid(row=1, column=0, padx=6, pady=6, sticky="w")

        ttk.Button(f, text="Экспорт в Excel (XLSX)", command=self._export_xlsx) \
            .grid(row=2, column=0, padx=6, pady=6, sticky="w")

        ttk.Button(f, text="Заполнить демо-данными", command=self._seed) \
            .grid(row=3, column=0, padx=6, pady=6, sticky="w")

    def _export_json(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON","*.json")])
        if not path: return
        try:
            self.db.export_json(path)
            messagebox.showinfo("OK", f"Экспортировано: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON","*.json")])
        if not path: return
        try:
            self.db.import_json(path)
            self._reload_clients(); self._reload_products(); self._reload_orders()
            messagebox.showinfo("OK", "Импорт завершён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _export_xlsx(self):
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        try:
            self.db.export_xlsx(path)
            messagebox.showinfo("OK", f"Сохранено: {path}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _seed(self):
        self.db.seed_demo()
        self._reload_clients(); self._reload_products(); self._reload_orders()




def run_gui(db_path: str = "orders.sqlite"):
    root = tk.Tk()
    root.title("Система учёта заказов")
    root.geometry("900x600")
    db = Database(db_path)
    db.init_schema()
    App(root, db)
    root.mainloop()
