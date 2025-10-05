from tortoise import fields, models


class Consultation(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="consultations")
    specialist_id = fields.IntField()
    service_id = fields.IntField()
    price = fields.IntField()
    is_successfull = fields.BooleanField(default=False)
    payment = fields.ForeignKeyField("models.Payment", related_name="consultations", null=True)
    is_verified_by_admin = fields.BooleanField(default=False)
    is_hidden = fields.BooleanField(default=False)
    name = fields.CharField(max_length=255, null=True)
    email = fields.CharField(max_length=255, null=True)
    tg_tag = fields.CharField(max_length=100, null=True)
    is_paid = fields.BooleanField(default=False)
    is_used = fields.BooleanField(default=False)

    class Meta:
        table = "consultation"


