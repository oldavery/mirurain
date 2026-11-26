"""Gear for rotating the bot status based on configured messages."""

import asyncio
import contextlib
from datetime import UTC, datetime
from itertools import cycle

from loguru import logger
from stoat import Presence, UserStatusEdit
from stoat.ext import commands
from tortoise.expressions import Q

from mirurain.enums import QueueStatus
from mirurain.tables import NotificationQueue
from mirurain.utilities.mirurain import MirurainBot
from mirurain.utilities.settings import settings


class StatusGear(commands.Gear):
    """Update the bot status to reflect current fan-out progress."""

    def __init__(self, bot: MirurainBot) -> None:
        """Initialise the status gear.

        Args:
            bot: Bot instance that owns the gear.
        """
        super().__init__()
        self.bot = bot
        self._status_task: asyncio.Task[None] | None = None
        self._messages = cycle(settings.status.messages)

    async def _status_loop(self) -> None:
        while not self.bot.closed:
            await asyncio.sleep(settings.status.sleep)
            try:
                if self.bot.me is None:
                    logger.debug("skipping status update due to partial me")
                    continue

                message = next(self._messages)

                if "{fanner.queue}" in message:
                    count = await NotificationQueue.filter(
                        Q(status=QueueStatus.QUEUED)
                        | Q(status=QueueStatus.RETRYING)
                        | Q(status=QueueStatus.PROCESSING)
                    ).count()
                    message = message.replace("{fanner.queue}", f"{(count):,}")

                if "{fanner.recently_completed}" in message:
                    count = await NotificationQueue.filter(
                        status=QueueStatus.COMPLETED,
                        updated_at__gte=datetime.now(UTC).replace(
                            hour=0,
                            minute=0,
                            second=0,
                            microsecond=0,
                        ),
                    ).count()
                    message = message.replace(
                        "{fanner.recently_completed}", f"{(count):,}"
                    )

                await self.bot.me.edit(
                    status=UserStatusEdit(text=message, presence=Presence.focus)
                )
                logger.debug(f"set status to '{message}'", extra={"message": message})
            except Exception:
                logger.exception("failed to update status message")

    async def gear_load(self) -> None:
        """Start the background task that periodically updates the bot's status."""
        if self._status_task is None or self._status_task.done():
            self._status_task = asyncio.create_task(self._status_loop())

    async def gear_unload(self) -> None:
        """Stop the background status-update task if it is running."""
        task = self._status_task
        if task is None:
            return

        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
