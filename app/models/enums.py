from enum import Enum


class SubscriptionType(str, Enum):
    FREE = "free"
    UNLIMITED = "unlimited"
    PREMIUM = "premium"
    GIFT = "gift"
    SPECIAL = "special"


class PaymentType(str, Enum):
    SUBSCRIPTION = "subscription"
    CONSULTATION = "consultation"
    MATERIAL = "material"
    GIFT = "gift"
    SERVICE = "service"
    OTHER = "other"


