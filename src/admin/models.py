from fastapi_admin.models import AbstractAdmin
from tortoise import fields

class Admin(AbstractAdmin):
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}#{self.username}"