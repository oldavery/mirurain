"""Tracked notification records for Mirurain."""

import datetime

from tortoise import fields, models

from mirurain.enums import Platform


class TrackedUser(models.Model):
    """Tracked user record for outbound notifications.

    Attributes:
        platform: Platform or network the user belongs to.
        canonical: Canonical identifier for the user.
        display_as: User-friendly representation of the user.
        channel: Channel to deliver notifications to.
        server: Server that owns the channel, or ``None`` for future group support.
        created_at: Timestamp when the record was created.
    """

    platform = fields.CharEnumField(Platform, max_length=32, index=True)

    canonical = fields.TextField()

    display_as = fields.TextField(null=True)

    channel: fields.Field[str] = fields.CharField(max_length=32)

    server: fields.Field[str | None] = fields.CharField(max_length=32, null=True)

    created_at: fields.Field[datetime.datetime] = fields.DatetimeField(
        auto_now_add=True, index=True
    )
