"""Notification queue table model for Mirurain."""

import datetime

from tortoise import fields, models

from mirurain.enums import Platform, QueueStatus


class NotificationQueue(models.Model):
    """Persistent queue entries used for outbound notification fan-out."""

    id: fields.Field[int] = fields.BigIntField(pk=True)

    # Processing state.
    status = fields.IntEnumField(QueueStatus, "Queued notification status.")
    attempts: fields.Field[int] = fields.IntField(default=0)

    # Record metadata.
    created_at: fields.Field[datetime.datetime] = fields.DatetimeField(
        auto_now_add=True, index=True
    )
    updated_at: fields.Field[datetime.datetime] = fields.DatetimeField(
        auto_now=True, index=True
    )
    leased_at: fields.Field[datetime.datetime | None] = fields.DatetimeField(
        null=True, index=True
    )
    claim_token: fields.Field[str | None] = fields.CharField(
        max_length=36, null=True, index=True
    )

    # Notification payload context.
    embed = fields.JSONField()
    server_id: fields.Field[str] = fields.CharField(max_length=32, index=True)
    channel_id: fields.Field[str] = fields.CharField(max_length=32, index=True)
    message_id: fields.Field[str | None] = fields.CharField(max_length=32, null=True)

    # Source-scoped identity fields.
    source = fields.CharEnumField(
        Platform, "Notification source platform.", max_length=32
    )
    source_post_canonical = fields.TextField()
    source_author_canonical = fields.TextField()
