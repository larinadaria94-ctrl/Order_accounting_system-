## Возможности

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

## Запуск

# установка необходимых модулей(при необходимости)
pip install -r order_manager\requirements.txt

# создать/обновить схему и залить демо-данные
python -m order_manager.main --seed

# запустить приложение
python -m order_manager.main

## Интерфейс
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/6d63d9cc5ec1660b722a80547eceb23af90e5dca/images/image.png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(1).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(2).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(3).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(4).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(5).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(6).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(7).png)
![image alt](https://github.com/larinadaria94-ctrl/Order_accounting_system-/blob/1c2d55d0a4ba652cf1b7d16d0c78b8202aa709b8/images/image%20(8).png)
