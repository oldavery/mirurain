"""Update queue timestamp indexing."""

from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields


class Migration(migrations.Migration):
    """Update queue timestamp indexing."""

    dependencies = [("models", "0002_auto_20260519_1608")]

    initial = False

    operations = [
        ops.AlterField(
            model_name="NotificationQueue",
            name="updated_at",
            field=fields.DatetimeField(db_index=True, auto_now=True, auto_now_add=False),
        ),
    ]
