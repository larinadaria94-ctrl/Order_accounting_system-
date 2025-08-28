# Возможности

- **Клиенты**
  - Добавление/поиск/удаление
  - Защита от дублей по e-mail/телефону
  - Валидация форматов e-mail/телефона
  - Поиск: **число → только по ID**, строка → по `name/email/phone/address`
  - Если ничего не найдено — отображаются все клиенты и показывается неблокирующее уведомление

- **Товары**
  - Добавление с проверкой цены (число `≥ 0`)
  - Удаление запрещено, если товар встречается в заказах

- **Заказы**
  - Формирование позиций (товар + количество)
  - Создание заказа на текущую дату
  - Таблица заказов с сортировкой по **дате** и **сумме** (собственный `merge_sort`)

- **Аналитика**
  - Топ-5 клиентов по числу заказов
  - Динамика заказов по датам
  - Граф связей клиентов по городам (узлы = **ID**, подписи = «Имя (Город)»)

- **Импорт/экспорт**
  - Полный дамп/восстановление **JSON**
  - **CSV** «дружелюбный к Excel» (CP1251, `sep=;`, телефоны/даты как текст)
  - **XLSX** (через `openpyxl`) с форматами столбцов

---

**Поток управления**:

- `main.py` → парсит флаги → `db.init_schema()` → либо `db.seed_demo()`, либо `run_gui(db_path)`
- `gui.py`/`App` создаёт вкладки и вызывает методы `db.py`/`analysis.py`
- `db.py` инкапсулирует `sqlite3.Connection` и все SQL-операции

---

## Модель данных (БД)

При старте создаётся схема SQLite:

- `clients(id, name, email, phone, address)`
- `products(id, name, price /*CHECK price≥0 рекомендовано*/)`
- `orders(id, client_id → clients.id ON DELETE CASCADE, date)`
- `order_items(id, order_id → orders.id ON DELETE CASCADE, product_id → products.id, quantity)`

**Внешние ключи** включены (`PRAGMA foreign_keys=ON`).  
Рекомендуются уникальные индексы на `clients.email` и `clients.phone` (в коде есть проверка дублей перед вставкой).

> **Важно:** в сводной выборке сумма заказа вычисляется как `SUM(oi.quantity * p.price)` из **текущих** цен в `products`. Если цена товара меняется, исторические суммы тоже изменятся. Чтобы «заморозить» цену, храните цену в `order_items` и используйте её в расчёте.

---

# Запуск

## установка необходимых модулей(при необходимости)
pip install -r order_manager\requirements.txt

## создать/обновить схему и залить демо-данные
python -m order_manager.main --seed

## запустить приложение
python -m order_manager.main

# Интерфейс
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/6d63d9cc5ec1660b722a80547eceb23af90e5dca/images/image.png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(1).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(2).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(3).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(4).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(5).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(6).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(7).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(8).png)


# Документация модулей и функций проекта

## `app.py` — лаунчер

**Назначение:** запускатель основного приложения (удобно для сборки в `.exe`).

### Функции
- **`main()` (косвенно)** — не определяет собственный `main`; импортирует `order_manager.main.main` и вызывает его при запуске файла напрямую.

---

## `order_manager/main.py` — точка входа (CLI)

**Назначение:** парсит аргументы, подготавливает БД и запускает GUI.

### Функции
- **`_default_db_path() -> str`**  
  Возвращает путь к файлу БД по умолчанию. Учитывает упакованный режим (frozen), чтобы класть БД рядом с исполняемым файлом.
- **`main()`**  
  CLI:
  - `--db PATH` — путь к SQLite-файлу (по умолчанию рядом с приложением).
  - `--seed` — инициализировать схему и наполнить демо-данными, затем выйти.  
  Логика:
  - При `--seed`: `Database(db).init_schema(); Database.seed_demo(); exit`.
  - Иначе: `run_gui(db)` — запуск графического интерфейса.

---

## `order_manager/gui.py` — графический интерфейс (Tkinter)

**Назначение:** собирает окно приложения, вкладки и логику взаимодействия с БД/аналитикой.

### Функции верхнего уровня
- **`run_gui(db_path: str = "orders.sqlite")`**  
  Создаёт `Tk`, открывает/инициализирует БД, монтирует `App` и запускает `mainloop()`.

### Классы
- **`class App(ttk.Frame)`** — основной виджет приложения.
  - **`__init__(self, master, db)`**  
    Сохраняет ссылку на `Database`, настраивает фрейм и вызывает `_build()`.
  - **`_build(self)`**  
    Создаёт `ttk.Notebook` и добавляет вкладки: Клиенты, Товары, Заказы, Аналитика, Администрирование.

#### Вкладка «Клиенты»
- **`_clients_tab(self, nb)`**  
  Размечает форму добавления клиента, панель поиска и таблицу (`Treeview`), кнопки действий.
- **`_save_client(self)`**  
  Читает поля, валидирует через `models.Client`, вызывает `db.add_client`, обновляет таблицу.
- **`_reload_clients(self, rows=None)`**  
  Очищает и заполняет таблицу клиентов: из `rows` или `db.list_clients()`.
- **`_find_clients(self, q=None, event=None)`**  
  Поиск: пусто → все клиенты; число → `db.get_client_by_id`; иначе → `db.find_clients`.  
  Если ничего не найдено — показываются все и выводится неблокирующее уведомление.
- **`_delete_client(self)`**  
  Удаляет выбранного клиента (`db.delete_client`) и обновляет таблицы клиентов/заказов.

#### Вкладка «Товары»
- **`_products_tab(self, nb)`**  
  Форма добавления товара, таблица, кнопка удаления.
- **`_save_product(self)`**  
  Валидирует название/цену, создаёт `models.Product`, добавляет через `db.add_product`, обновляет таблицу и комбобоксы заказов.
- **`_reload_products(self)`**  
  Перечитывает список товаров из БД и перерисовывает таблицу.
- **`_delete_product(self)`**  
  Удаляет выбранный товар; если товар используется в заказах — показывает ошибку.
- **`_refresh_order_combos(self)`**  
  Обновляет комбобоксы клиента/товара в форме создания заказа.

#### Вкладка «Заказы»
- **`_orders_tab(self, nb)`**  
  Форма выбора клиента/товара/количества, мини-таблица позиций, сортировка заказов и таблица заказов, кнопка удаления.
- **`_add_to_order(self)`**  
  Добавляет выбранную позицию `(product_id, qty)` во временный список и в мини-таблицу.
- **`_create_order(self)`**  
  Создаёт заказ: `db.create_order(client_id, now_date_str(), items)`, очищает корзину, обновляет таблицу заказов.
- **`_reload_orders(self, rows=None)`**  
  Перерисовывает таблицу заказов; безопасно приводит `total` к `float` и округляет.
- **`_sort_orders(self)`**  
  Получает текущие строки, приводит типы и сортирует через `utils.merge_sort` по выбранному ключу (`date`/`total`).
- **`_delete_order(self)`**  
  Удаляет выделенный заказ (`db.delete_order`) и обновляет таблицу.

#### Вкладка «Аналитика»
- **`_analysis_tab(self, nb)`**  
  Кнопки: `analysis.plot_top5_clients(conn)`, `analysis.plot_orders_timeline(conn)`, `analysis.client_graph_by_city(conn)`.

#### Вкладка «Администрирование»
- **`_admin_tab(self, nb)`**  
  Кнопки: экспорт/импорт JSON, экспорт CSV (CP1251), экспорт XLSX, сидинг демо-данных.
- **`_export_json(self)` / `_import_json(self)`**  
  Диалог выбора файла, вызов `db.export_json/import_json`; после импорта — перерисовка таблиц.
- **`_export_xlsx(self)`**  
  Диалог сохранения и вызов `db.export_xlsx`.
- **`_seed(self)`**  
  `db.seed_demo()` и обновление таблиц.

---

## `order_manager/db.py` — доступ к данным (SQLite) + импорт/экспорт

**Назначение:** инкапсулирует соединение `sqlite3`, определяет схему и предоставляет CRUD/API-методы.

### Константы
- **`DB_SCHEMA`**  
  SQL-скрипт: `PRAGMA foreign_keys=ON` и `CREATE TABLE IF NOT EXISTS` для `clients`, `products`, `orders`, `order_items`.

### Класс `Database`
- **`__init__(self, path="orders.sqlite")`**  
  Сохраняет путь; соединение открывается лениво.
- **`connect(self)`**  
  Открывает `sqlite3.connect(path)` и включает `row_factory=sqlite3.Row`.
- **`conn` (property) -> sqlite3.Connection**  
  Гарантирует открытое соединение и возвращает его.
- **`init_schema(self)`**  
  Выполняет `DB_SCHEMA` через `executescript` и коммитит.

#### Клиенты
- **`add_client(self, name, email, phone, address) -> int`**  
  Проверяет дубли по email/телефону. Вставляет клиента, `commit`, возвращает `lastrowid`. При дублях — `ValueError`.
- **`list_clients(self) -> list[Row]`**  
  Возвращает всех клиентов по `id`.
- **`find_clients(self, q: str) -> list[Row]`**  
  Поиск `LIKE` по `name/email/phone/address`.
- **`get_client_by_id(self, cid: int) -> list[Row]`**  
  Точное совпадение по `id`.

#### Товары
- **`add_product(self, name, price) -> int`**  
  Вставляет товар (цена приводится к `float`), коммит, `lastrowid`.
- **`list_products(self) -> list[Row]`**  
  Все товары по `id`.

#### Заказы
- **`create_order(self, client_id, date, items) -> int`**  
  Вставляет заказ (шапку), затем пакетно вставляет позиции `(order_id, product_id, quantity)`, коммит, возвращает `order_id`.
- **`list_orders(self) -> list[Row]`**  
  Сводная выборка: `o.id`, `o.date`, `c.name AS client`, `SUM(oi.quantity*p.price) AS total`, `SUM(oi.quantity) AS total_qty`.  
  *Важно:* сумма считается из **текущих** цен `products`.
- **`order_items(self, order_id) -> list[Row]`**  
  Позиции заказа с `line_total = price*quantity`.

#### Удаление
- **`delete_client(self, client_id)`**  
  Удаляет клиента; каскадом удалятся его заказы и позиции.
- **`delete_order(self, order_id)`**  
  Удаляет заказ; позиции удалятся каскадом.
- **`delete_product(self, product_id)`**  
  Проверяет, используется ли товар в `order_items`; если да — `ValueError`, иначе удаляет.

#### Импорт/экспорт/сидинг
- **`export_json(self, out_path)`**  
  Полный дамп 4 таблиц в JSON (UTF-8, `ensure_ascii=False`, `indent=2`).
- **`import_json(self, in_path)`**  
  Очищает таблицы (сначала дочерние), затем `executemany` для восстановления данных, `commit`.
- **`export_csv(self, folder="export_csv", *, encoding="cp1251", excel_friendly=True)`**  
  Выгружает по одному CSV на таблицу. Если `excel_friendly=True`:  
  — пишет первую строку `sep=;`,  
  — сохраняет `phone`/`date` как текст (префикс `'`),  
  — использует `;` как разделитель.  
  По умолчанию — `cp1251` для корректного открытия в Excel.
- **`export_xlsx(self, out_path="export.xlsx")`**  
  Создаёт книгу Excel с листами на каждую таблицу, применяет форматы (`price: 0.00`, `date: yyyy-mm-dd`) и ширины колонок.
- **`seed_demo(self)`**  
  Если клиентов/товаров нет — добавляет демо-клиентов/товары и 4 заказа с фиксированными датами.

---

## `order_manager/models.py` — доменные модели и валидация

**Назначение:** описывает объекты предметной области и их инварианты (инкапсуляция/полиморфизм).

### Базовый класс (для наследования)
- **`class BaseModel`**
  - `to_dict(self) -> dict` — сериализация (для dataclass через `asdict`).
  - `from_dict(cls, d: dict)` — фабрика: создать объект из словаря.

### Человек/Клиент
- **`@dataclass class Person(BaseModel)`**  
  Поле: `name: str`.
- **`class Client(Person)`**
  - `__init__(name, email, phone, address="")` — приватные `_email/_phone`; назначение через свойства с валидацией.
  - `email` (`property`) — геттер/сеттер; сеттер валидирует `validate_email`, иначе `ValueError`.
  - `phone` (`property`) — геттер/сеттер; сеттер валидирует `validate_phone`, иначе `ValueError`.
  - `to_dict()` — сериализует публичные `email/phone/address` (не `_email/_phone`).
  - `from_dict(cls, d)` — фабричный метод из словаря.

### Товар
- **`@dataclass class Product(BaseModel)`**
  - Поля: `name: str`, `price: float`.
  - `__post_init__` — `self.price = safe_float(self.price)`, запрет `price < 0` (`ValueError`).

### Позиция заказа
- **`@dataclass class OrderItem(BaseModel)`**
  - Поля: `product_id: int`, `quantity: int`.
  - `__post_init__` — приводит к `int`, требует `quantity > 0`.

### Заказ
- **`@dataclass class Order(BaseModel)`**
  - Поля: `client_id: int`, `date: str`, `items: list[OrderItem]`.
  - `total_positions` (`property`) — сумма количеств всех позиций.
  - `to_dict()` — сериализует вложенные `OrderItem` в список словарей.
  - `simple(client_id, items, date=None)` — фабрика: дата по умолчанию `utils.now_date_str()`.

---

## `order_manager/analysis.py` — аналитика и визуализации

**Назначение:** подготавливает агрегированные выборки и строит графики.

### Вспомогательная функция
- **`_df(sql: str, conn) -> pd.DataFrame`**  
  Выполняет SQL на переданном соединении и возвращает DataFrame.

### Аналитика
- **`top5_clients_by_orders(conn) -> DataFrame`**  
  Возвращает топ-5 клиентов по числу заказов: колонки `name`, `orders`.
- **`orders_per_day(conn) -> DataFrame`**  
  Возвращает количество заказов по дням: колонки `date`, `cnt`.

### Графики
- **`plot_top5_clients(conn) -> DataFrame`**  
  Строит bar-chart по `top5_clients_by_orders` (и возвращает исходный DataFrame).
- **`plot_orders_timeline(conn) -> DataFrame`**  
  Строит line-chart по `orders_per_day` (и возвращает исходный DataFrame).
- **`client_graph_by_city(conn) -> nx.Graph`**  
  Строит граф: узлы = **ID клиентов**, подписи = «Имя (Город)». Рёбра между клиентами из одного города. Рисует через `matplotlib`, возвращает объект `Graph`.

---

## `order_manager/utils.py` — общие утилиты

**Назначение:** валидации, сортировки и вспомогательные функции.

### Константы (regex)
- **`EMAIL_RE`**, **`PHONE_RE`** — регулярные выражения для базовой проверки email/телефона.

### Функции
- **`validate_email(email: str) -> bool`** — проверка строки по `EMAIL_RE`.
- **`validate_phone(phone: str) -> bool`** — проверка строки по `PHONE_RE`.
- **`safe_float(x, default=0.0) -> float`** — безопасное приведение к `float`; при ошибке возвращает `default`.
- **`merge_sort(items, key, reverse=False) -> list`** — рекурсивная стабильная сортировка «разделяй-и-властвуй». Используется в GUI для сортировки заказов.
- **`now_date_str() -> str`** — текущая дата в формате `YYYY-MM-DD`.

---

## Тесты

### `order_manager/tests/test_models.py`
**Назначение:** проверяет модели.
- `test_client_validation` — корректность валидации email/телефона у `Client` (ошибки на некорректных значениях).
- `test_product_price` — преобразование цены к `float` и запрет отрицательных значений у `Product`.
- `test_order_total_positions` — корректность вычисляемого свойства `Order.total_positions`.

### `order_manager/tests/test_analysis.py`
**Назначение:** smoke-test аналитики.
- `setUp` — поднимает in-memory БД, инициализирует схему и демо-данные.
- `test_top5` — DataFrame не пустой, содержит колонки `name`, `orders`.
- `test_orders_per_day` — DataFrame не пустой, содержит колонку `cnt`.

---
