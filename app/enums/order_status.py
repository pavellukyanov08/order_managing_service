from enum import StrEnum, unique


@unique
class OrderStatus(StrEnum):
    PENDING = "Ожидание"
    PAID = "Оплачен"
    SHIPPED = "Доставлен"
    CANCELED = "Отменён"
