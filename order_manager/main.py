"""
Точка входа. Запуск GUI:  python -m order_manager.main
"""
from __future__ import annotations
import argparse
from .gui import run_gui
from .db import Database

from pathlib import Path
import sys

def _default_db_path() -> str:
    base_dir = Path(sys.executable).parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
    return str(base_dir / "orders.sqlite")

def main():
    parser = argparse.ArgumentParser(description="Order Manager")
    parser.add_argument("--db", default="orders.sqlite", help="Путь к SQLite БД")
    parser.add_argument("--seed", action="store_true", help="Заполнить демо-данными и выйти")
    args = parser.parse_args()

    if args.seed:
        db = Database(args.db); db.init_schema(); db.seed_demo()
        print("Демо-данные добавлены.")
        return

    run_gui(args.db)

if __name__ == "__main__":
    main()
