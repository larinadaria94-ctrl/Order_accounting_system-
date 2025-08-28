import sqlite3
import unittest
from order_manager.db import Database
from order_manager import analysis as anl


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.db.init_schema()
        self.db.seed_demo()
        self.conn: sqlite3.Connection = self.db.conn

    def test_top5(self):
        df = anl.top5_clients_by_orders(self.conn)
        self.assertTrue("name" in df.columns and "orders" in df.columns)
        self.assertTrue(len(df) >= 1)

    def test_orders_per_day(self):
        df = anl.orders_per_day(self.conn)
        self.assertTrue(len(df) >= 1)
        self.assertTrue("cnt" in df.columns)

if __name__ == "__main__":
    unittest.main()
