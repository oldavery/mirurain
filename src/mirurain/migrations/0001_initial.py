from orjson import loads
from tortoise import fields, migrations
from tortoise.fields.data import JSON_DUMPS
from tortoise.migrations import operations as ops

from mirurain.enums.platform import Platform
from mirurain.enums.queue import QueueStatus


class Migration(migrations.Migration):
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
                        description="Queued notification status.",
                        enum_type=QueueStatus,
                        generated=False,
                    ),
                ),
                ("attempts", fields.IntField(default=0)),
                (
                    "created_at",
                    fields.DatetimeField(
                        db_index=True, auto_now=False, auto_now_add=True
                    ),
                ),
                (
                    "updated_at",
                    fields.DatetimeField(
                        db_index=True, auto_now=True, auto_now_add=False
                    ),
                ),
                (
                    "leased_at",
                    fields.DatetimeField(
                        null=True, db_index=True, auto_now=False, auto_now_add=False
                    ),
                ),
                (
                    "claim_token",
                    fields.CharField(null=True, db_index=True, max_length=36),
                ),
                ("embed", fields.JSONField(encoder=JSON_DUMPS, decoder=loads)),
                ("server_id", fields.CharField(db_index=True, max_length=32)),
                ("channel_id", fields.CharField(db_index=True, max_length=32)),
                ("message_id", fields.CharField(null=True, max_length=32)),
                (
                    "source",
                    fields.CharEnumField(
                        description="Notification source platform.",
                        enum_type=Platform,
                        max_length=32,
                    ),
                ),
                ("source_post_canonical", fields.TextField(unique=False)),
                ("source_author_canonical", fields.TextField(unique=False)),
            ],
            options={
                "table": "notificationqueue",
                "app": "models",
                "pk_attr": "id",
                "table_description": "Persistent queue entries used for outbound notification fan-out.",
            },
            bases=["Model"],
        ),
        ops.CreateModel(
            name="TrackedUser",
            fields=[
                (
                    "id",
                    fields.IntField(
                        generated=True, primary_key=True, unique=True, db_index=True
                    ),
                ),
                (
                    "platform",
                    fields.CharEnumField(
                        db_index=True,
                        description="BLUESKY: bluesky\nMASTODON: mastodon\nNOSTR: nostr\nTUMBLR: tumblr\nTWITTER: twitter\nNONE: none",
                        enum_type=Platform,
                        max_length=32,
                    ),
                ),
                ("canonical", fields.TextField(unique=False)),
                ("display_as", fields.TextField(null=True, unique=False)),
                ("channel", fields.CharField(max_length=32)),
                ("server", fields.CharField(null=True, max_length=32)),
                (
                    "created_at",
                    fields.DatetimeField(
                        db_index=True, auto_now=False, auto_now_add=True
                    ),
                ),
            ],
            options={
                "table": "trackeduser",
                "app": "models",
                "pk_attr": "id",
                "table_description": "Tracked user record for outbound notifications.",
            },
            bases=["Model"],
        ),
    ]
