from tortoise import fields, models
from .enums import SubscriptionType, PaymentType


class User(models.Model):
    tg_id = fields.BigIntField(pk=True)
    username = fields.CharField(max_length=100, null=True)
    full_name = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    last_question = fields.DatetimeField(null=True)
    chat_id = fields.IntField(default=0)
    wait_for = fields.IntField(default=0)

    class Meta:
        table = "users"


class Payment(models.Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation["User"] = fields.ForeignKeyField("models.User", related_name="payments")
    price = fields.IntField()
    subscription_type = fields.CharEnumField(enum_type=SubscriptionType, max_length=50, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    paid_at = fields.DatetimeField(null=True)
    is_paid = fields.BooleanField(default=False)
    payment_type = fields.CharEnumField(enum_type=PaymentType, max_length=50, default=PaymentType.SUBSCRIPTION)
    parent_payment: fields.ForeignKeyNullableRelation["Payment"] = fields.ForeignKeyField("models.Payment", related_name="child_payments", null=True)
    material_ids = fields.JSONField(null=True)  # JSON массив с ID материалов

    class Meta:
        table = "payments"


class Subscription(models.Model):
    id = fields.IntField(pk=True)
    payment = fields.ForeignKeyField("models.Payment", null=True)
    user = fields.OneToOneField("models.User", related_name="subscription")
    created_at = fields.DatetimeField(auto_now_add=True)
    expires_at = fields.DatetimeField(null=True)
    subscription_type = fields.CharEnumField(enum_type=SubscriptionType, default=SubscriptionType.FREE)
    is_active = fields.BooleanField(default=True)

    class Meta:
        table = "subscriptions"


