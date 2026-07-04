"""Add queue metadata fields and table descriptions."""

from tortoise import migrations
from tortoise.migrations import operations as ops
from tortoise import fields


class Migration(migrations.Migration):
    """Add lease tracking and message metadata fields."""

    dependencies = [("models", "0001_initial")]

    initial = False

    operations = [
        ops.AlterModelOptions(
            name="NotificationQueue",
            options={
                "table": "notificationqueue",
                "app": "models",
                "pk_attr": "id",
                "table_description": "Persistent queue entries used for outbound notification fan-out.",
            },
        ),
        ops.AddField(
            model_name="NotificationQueue",
            name="claim_token",
            field=fields.CharField(null=True, db_index=True, max_length=36),
        ),
        ops.AddField(
            model_name="NotificationQueue",
            name="leased_at",
            field=fields.DatetimeField(
                null=True, db_index=True, auto_now=False, auto_now_add=False
            ),
        ),
        ops.AddField(
            model_name="NotificationQueue",
            name="message_id",
            field=fields.CharField(null=True, max_length=32),
        ),
    ]
