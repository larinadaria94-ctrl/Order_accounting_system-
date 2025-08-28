from __future__ import annotations
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from typing import Optional


def _df(sql: str, conn: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query(sql, conn)


def top5_clients_by_orders(conn: sqlite3.Connection) -> pd.DataFrame:
    sql = """
    SELECT c.name, COUNT(o.id) AS orders
    FROM clients c
    LEFT JOIN orders o ON o.client_id=c.id
    GROUP BY c.id, c.name
    ORDER BY orders DESC, c.name
    LIMIT 5
    """
    return _df(sql, conn)


def orders_per_day(conn: sqlite3.Connection) -> pd.DataFrame:
    sql = """
    SELECT date, COUNT(*) AS cnt
    FROM orders
    GROUP BY date
    ORDER BY date
    """
    return _df(sql, conn)


def client_graph_by_city(conn: sqlite3.Connection):
    sql = "SELECT id, name, COALESCE(address, '') AS city FROM clients"
    df = _df(sql, conn)

    G = nx.Graph()
    labels = {}

    for _, r in df.iterrows():
        cid = int(r["id"])
        city = r["city"] or ""
        G.add_node(cid, city=city)
        labels[cid] = f'{r["name"]} ({city})' if city else r["name"]

    for city, g in df.groupby("city"):
        ids = list(map(int, g["id"]))
        for i in range(len(ids) - 1):
            for j in range(i + 1, len(ids)):
                G.add_edge(ids[i], ids[j])

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=False, node_size=1200, alpha=0.9)
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10)
    plt.title("Граф связей клиентов по городам")
    plt.tight_layout()
    plt.show()
    return G



def plot_top5_clients(conn: sqlite3.Connection):
    df = top5_clients_by_orders(conn)
    plt.figure(figsize=(6, 4))
    sns.barplot(data=df, x="name", y="orders")
    plt.title("Топ-5 клиентов по количеству заказов")
    plt.xlabel("Клиент")
    plt.ylabel("Заказы")
    plt.tight_layout()
    plt.show()
    return df


def plot_orders_timeline(conn: sqlite3.Connection):
    df = orders_per_day(conn)
    plt.figure(figsize=(7, 4))
    sns.lineplot(data=df, x="date", y="cnt", marker="o")
    plt.title("Динамика количества заказов по датам")
    plt.xlabel("Дата")
    plt.ylabel("Количество заказов")
    plt.tight_layout()
    plt.show()
    return df
