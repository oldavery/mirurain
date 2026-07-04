"""Initial schema migration for Mirurain queue storage."""

from orjson import loads
from tortoise import fields, migrations
from tortoise.fields.data import JSON_DUMPS
from tortoise.migrations import operations as ops

from mirurain.enums.platform import Platform
from mirurain.enums.queue import QueueStatus


class Migration(migrations.Migration):
    """Create the first notification queue table."""

    initial = True

    operations = [
        ops.CreateModel(
            name="NotificationQueue",
            fields=[
                (
                    "id",
                    fields.BigIntField(
                        generated=True, primary_key=True, unique=True, db_index=True
                    ),
                ),
                (
                    "status",
                    fields.IntEnumField(
                        description="The status of the queued notification.",
                        enum_type=QueueStatus,
                        generated=False,
                    ),
                ),
                ("attempts", fields.IntField(default=0)),
                (
                    "created_at",
                    fields.DatetimeField(db_index=True, auto_now=False, auto_now_add=True),
                ),
                ("updated_at", fields.DatetimeField(auto_now=True, auto_now_add=False)),
                ("embed", fields.JSONField(encoder=JSON_DUMPS, decoder=loads)),
                ("server_id", fields.CharField(db_index=True, max_length=32)),
                ("channel_id", fields.CharField(db_index=True, max_length=32)),
                (
                    "source",
                    fields.CharEnumField(
                        description="The source of the notification.",
                        enum_type=Platform,
                        max_length=32,
                    ),
                ),
                ("source_post_canonical", fields.TextField(unique=False)),
                ("source_author_canonical", fields.TextField(unique=False)),
            ],
            options={"table": "notificationqueue", "app": "models", "pk_attr": "id"},
            bases=["Model"],
        ),
    ]
