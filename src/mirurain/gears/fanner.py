"""Fan-out worker gear for delivering queued notifications."""

# TODO (Avery): Add support for multiple workers

import asyncio
import contextlib
import datetime
from uuid import uuid4

import stoat
from loguru import logger
from stoat import (
    Forbidden,
    GroupChannel,
    NotFound,
    SendableEmbed,
    TextChannel,
    VoiceChannel,
)
from stoat.ext import commands
from tortoise.expressions import Q
from tortoise.transactions import in_transaction

from mirurain.enums import QueueStatus
from mirurain.tables import NotificationQueue
from mirurain.utilities.mirurain import MirurainBot
from mirurain.utilities.settings import settings


class FannerGear(commands.Gear):
    """Fan-out gear for processing queued notifications."""

    def __init__(self, bot: MirurainBot) -> None:
        """Initialise the fan-out gear.

        Args:
            bot: Bot instance that owns the gear.
        """
        super().__init__()
        self.bot = bot
        self._fan_task: asyncio.Task[None] | None = None

    async def _queue_get(
        self, amount: int, lease: int = 300
    ) -> list[NotificationQueue]:
        """Retrieve queued notifications up to the specified amount.

        Picks the oldest entries in QUEUED, RETRYING, or expired-lease
        PROCESSING states and marks them PROCESSING with a claim token.

        Args:
            amount: Maximum notifications to claim.
            lease: Lease duration in seconds before expired leases become
                reclaimable. Defaults to 300.

        Returns:
            The claimed notification records, ordered by creation time.

        Raises:
            ValueError: If *amount* or *lease* is less than 1.
            asyncio.CancelledError: If the database connection is closing.
            Exception: For other unexpected database errors.
        """
        if amount < 1:
            raise ValueError("amount must be >= 1")

        if lease < 1:
            raise ValueError("lease must be >= 1")

        now = datetime.datetime.now(datetime.UTC)
        leased_cutoff = now - datetime.timedelta(seconds=lease)
        token = str(uuid4())

        claimable = (
            Q(status=QueueStatus.QUEUED)
            | Q(status=QueueStatus.RETRYING)
            | (
                Q(status=QueueStatus.PROCESSING)
                & (Q(leased_at__lt=leased_cutoff) | Q(leased_at__isnull=True))
            )
        )
        try:
            async with in_transaction() as conn:
                candidate_ids = await (
                    NotificationQueue
                    .filter(claimable)
                    .using_db(conn)
                    .order_by("created_at")
                    .limit(amount)
                    .values_list("id", flat=True)
                )
                if not candidate_ids:
                    return []

                await (
                    NotificationQueue
                    .filter(id__in=candidate_ids)
                    .filter(claimable)
                    .using_db(conn)
                    .update(
                        status=QueueStatus.PROCESSING,
                        leased_at=now,
                        claim_token=token,
                    )
                )

                return await (
                    NotificationQueue
                    .filter(status=QueueStatus.PROCESSING, claim_token=token)
                    .using_db(conn)
                    .order_by("created_at")
                )

        except Exception as exc:
            s = str(exc).lower()
            if (
                ("pool" in s and ("closing" in s or "closed" in s))
                or ("connection" in s and ("closing" in s or "closed" in s))
                or "is closing" in s
            ):
                logger.warning("database connection closing; aborted queue gather")
                raise asyncio.CancelledError() from exc

            raise Exception from exc

    async def _mark_completed(self, queue_id: int, token: str) -> bool:
        """Mark a claimed queue entry as completed.

        Args:
            queue_id: Queue entry identifier.
            token: Claim token for the lease.

        Returns:
            bool: True if the queue entry was updated.
        """
        updated = await NotificationQueue.filter(
            id=queue_id,
            status=QueueStatus.PROCESSING,
            claim_token=token,
        ).update(
            status=QueueStatus.COMPLETED,
            claim_token=None,
            leased_at=None,
        )
        return updated == 1

    async def _mark_retry(self, queue_id: int, token: str) -> bool:
        """Mark a claimed queue entry for retry.

        Args:
            queue_id: Queue entry identifier.
            token: Claim token for the lease.

        Returns:
            bool: True if the queue entry was updated.
        """
        updated = await NotificationQueue.filter(
            id=queue_id,
            status=QueueStatus.PROCESSING,
            claim_token=token,
        ).update(
            status=QueueStatus.RETRYING,
            claim_token=None,
            leased_at=None,
        )
        return updated == 1

    async def _mark_failed(self, queue_id: int, token: str) -> bool:
        """Mark a claimed queue entry as failed.

        Args:
            queue_id: Queue entry identifier.
            token: Claim token for the lease.

        Returns:
            bool: True if the queue entry was updated.
        """
        updated = await NotificationQueue.filter(
            id=queue_id,
            status=QueueStatus.PROCESSING,
            claim_token=token,
        ).update(
            status=QueueStatus.FAILED,
            claim_token=None,
            leased_at=None,
        )
        return updated == 1

    async def _heartbeat(self, queue_id: int, token: str) -> bool:
        """Refresh the lease on a claimed queue entry.

        Args:
            queue_id: Queue entry identifier.
            token: Claim token for the lease.

        Returns:
            bool: True if the queue entry was updated.
        """
        now = datetime.datetime.now(datetime.UTC)
        updated = await NotificationQueue.filter(
            id=queue_id,
            status=QueueStatus.PROCESSING,
            claim_token=token,
        ).update(leased_at=now)
        return updated == 1

    async def process(self, notification: NotificationQueue) -> None:
        """Process a single queued notification.

        Args:
            notification: Queue entry to process.
        """
        token = notification.claim_token
        assert token is not None

        if notification.attempts > settings.fanner.max_retries:
            await self._mark_failed(notification.id, token)
            logger.warning(
                f"failed {notification.id} after {notification.attempts} for going above {settings.fanner.max_retries}"
            )
            return

        channel = self.bot.get_channel(notification.channel_id)
        if channel is None:
            try:
                channel = await self.bot.fetch_channel(notification.channel_id)
            except Forbidden:
                logger.exception(
                    f"failed to get destination {notification.channel_id} due to forbidden error"
                )
                await self._mark_retry(notification.id, token)
                return
            except NotFound:
                logger.exception(
                    f"failed to get destination {notification.channel_id} due to it no longer existing"
                )
                await self._mark_failed(notification.id, token)
                return
            except Exception:
                logger.exception(
                    f"failed to get destination {notification.id} due to unhandled error"
                )
                await self._mark_retry(notification.id, token)
                return

        if not isinstance(
            channel, (GroupChannel, TextChannel, VoiceChannel)
        ):  # TODO (Avery): Find possible paths to avoid hardcoding channels to reduce maintenance
            logger.warning(f"{notification.id} failed due to incompatible channel type")
            await self._mark_failed(notification.id, token)
            return

        try:
            raw = notification.embed
            if (
                raw.get("colour", None) is not None
            ):  # handle stoat.py inconsistent naming
                raw["color"] = raw.get("colour")
                del raw["colour"]
            embed = SendableEmbed(**raw)
        except TypeError:
            logger.exception(f"{notification.id} failed due to invalid embed payload")
            await self._mark_failed(notification.id, token)
            return

        try:
            await channel.send(
                embeds=[embed],
                mention_everyone=False,
                silent=True,
            )

        except stoat.Forbidden:
            logger.exception(
                f"failed to push to {notification.channel_id} when processing {notification.id} due to forbidden error"
            )
            await self._mark_retry(notification.id, token)
            return

        except stoat.NotFound:
            logger.exception(
                f"failed to push {notification.id} destination {notification.channel_id} no longer exists"
            )
            await self._mark_failed(notification.id, token)
            return

        await self._mark_completed(notification.id, token)

        logger.info(f"{notification.id} processed")

    async def _fan_loop(self) -> None:
        """Background loop that polls the queue and dispatches notifications."""
        while not self.bot.closed:
            await asyncio.sleep(settings.fanner.sleep)

            try:
                queue = await self._queue_get(3)
            except asyncio.CancelledError:
                logger.info("notification fanner shutting down due to closure")
                break

            if len(queue) < 1:
                logger.debug("gather resulted in no notifications, sleeping")
                continue

            for notification in queue:
                try:
                    await self.process(notification)
                except Exception:
                    logger.exception(f"{notification.id} processing failed")
                    if notification.claim_token is not None:
                        await self._mark_retry(
                            notification.id,
                            notification.claim_token,
                        )

    async def gear_load(self) -> None:
        """Start the background task that fans out queued notifications."""
        if self._fan_task is None or self._fan_task.done():
            self._fan_task = asyncio.create_task(self._fan_loop())

    async def gear_unload(self) -> None:
        """Stop the background fan-out task if it is running."""
        task = self._fan_task
        if task is None:
            return

        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task
