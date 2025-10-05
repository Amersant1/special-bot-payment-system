from tortoise import fields, models


class Material(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    file_id = fields.CharField(max_length=255)
    file_type = fields.CharField(max_length=20)
    access_level = fields.CharField(max_length=20, default="premium")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "material"


