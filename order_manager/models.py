from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from .utils import validate_email, validate_phone, safe_float, now_date_str


class BaseModel:
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]):
        return cls(**d)


@dataclass
class Person(BaseModel):
    name: str


class Client(Person):
    def __init__(self, name: str, email: str, phone: str, address: str = ""):
        super().__init__(name=name)
        self._email = ""
        self._phone = ""
        self.address = address
        self.email = email
        self.phone = phone

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if value and not validate_email(value):
            raise ValueError("Некорректный email")
        self._email = value or ""

    @property
    def phone(self) -> str:
        return self._phone

    @phone.setter
    def phone(self, value: str):
        if value and not validate_phone(value):
            raise ValueError("Некорректный телефон")
        self._phone = value or ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name, "email": self.email,
            "phone": self.phone, "address": self.address
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Client":
        return cls(**d)


@dataclass
class Product(BaseModel):
    name: str
    price: float

    def __post_init__(self):
        self.price = safe_float(self.price)
        if self.price < 0:
            raise ValueError("Цена не может быть отрицательной")


@dataclass
class OrderItem(BaseModel):
    product_id: int
    quantity: int

    def __post_init__(self):
        self.quantity = int(self.quantity)
        if self.quantity <= 0:
            raise ValueError("Количество должно быть > 0")


@dataclass
class Order(BaseModel):
    client_id: int
    date: str
    items: List[OrderItem]

    @property
    def total_positions(self) -> int:
        return sum(it.quantity for it in self.items)

    def to_dict(self) -> Dict[str, Any]:
        return {"client_id": self.client_id, "date": self.date,
                "items": [it.to_dict() for it in self.items]}

    @classmethod
    def simple(cls, client_id: int, items: List[OrderItem], date: Optional[str] = None):
        return cls(client_id=client_id, date=date or now_date_str(), items=items)
