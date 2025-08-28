import unittest
from order_manager.models import Client, Product, OrderItem, Order

class TestModels(unittest.TestCase):
    def test_client_validation(self):
        c = Client("Иван", "ivan@example.com", "+79991112233", "Москва")
        self.assertEqual(c.email, "ivan@example.com")
        with self.assertRaises(ValueError):
            c.email = "bad@"
        with self.assertRaises(ValueError):
            c.phone = "123"

    def test_product_price(self):
        self.assertEqual(Product("X", "10.5").price, 10.5)
        with self.assertRaises(ValueError):
            Product("X", -1)

    def test_order_total_positions(self):
        o = Order.simple(1, [OrderItem(2, 3), OrderItem(3, 1)])
        self.assertEqual(o.total_positions, 4)

if __name__ == "__main__":
    unittest.main()
