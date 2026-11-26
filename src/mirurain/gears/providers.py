"""Provider gear module for Mirurain."""

import asyncio
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any

from loguru import logger
from stoat.ext import commands

from mirurain.enums import Platform
from mirurain.providers import providers
from mirurain.tables import NotificationQueue
from mirurain.utilities.mirurain import MirurainBot
from mirurain.utilities.settings import settings

if TYPE_CHECKING:
    from mirurain.classes.provider import Provider


class ProviderGear(commands.Gear):
    """Manage provider lifecycles and persist queued notifications."""

    def __init__(self, bot: MirurainBot) -> None:
        """Initialise provider management state.

        Args:
            bot: Bot instance that owns the gear.
        """
        self.bot = bot
        self.loadedProviders: dict[Platform, Provider] = {}
        self._queue: asyncio.Queue[NotificationQueue] = asyncio.Queue()
        self._tasks: dict[Platform, asyncio.Task[None]] = {}
        self._signals: dict[Platform, asyncio.Event] = {}
        self._collector: asyncio.Task[None] | None = None

    async def _run_task(
        self,
        platform: Platform,
        func: Callable[[asyncio.Event], Coroutine[Any, Any, None]],
    ) -> None:
        self._signals[platform] = asyncio.Event()

        task = asyncio.create_task(
            func(self._signals[platform]),
            name=f"provider:{platform.name}",
        )
        self._tasks[platform] = task
        task.add_done_callback(self._task_done)

        logger.info(f"registered {platform.name} task")

    async def _stop_task(self, platform: Platform) -> None:
        task = self._tasks[platform]

        self._signals[platform].set()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception(f"{platform.name} failed to gracefully shutdown")

    def _task_done(self, fn: asyncio.Task[None]) -> None:
        platform = Platform[fn.get_name().split(":")]
        self._tasks.pop(platform)

        try:
            fn.result()
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception(f"{platform} provider failed")

    async def gear_load(self) -> None:
        """Start enabled providers and the queue collector loop."""
        if self._collector is None or self._collector.done():
            self._collector = asyncio.create_task(self._collector_loop())

        for provider in providers:
            p = provider(self.bot.state, self._queue)
            if self.loadedProviders.get(p.platform, None) is not None:
                logger.critical(
                    f"attempted to load {type(p).__qualname__} as {p.platform} but platform already exists from {type(self.loadedProviders[p.platform]).__qualname__}"
                )
                continue

            self.loadedProviders[p.platform] = p
            await self._run_task(p.platform, p.run)

    async def _collect(self) -> None:
        """Bulk-create pending notifications in the database queue."""
        notifications = []

        while True:
            try:
                notifications.append(self._queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        if len(notifications) < 1:
            return

        await NotificationQueue.bulk_create(notifications)

        logger.info(f"dumped {len(notifications)} to database queue")

    async def _collector_loop(self) -> None:
        while not self.bot.closed:
            await asyncio.sleep(settings.fanner.sleep)
            await self._collect()

    async def gear_unload(self) -> None:
        """Stop providers and flush pending notifications to storage."""
        if self._collector is not None and not self._collector.cancelled():
            self._collector.cancel()

            try:
                await self._collector
            except asyncio.CancelledError:
                pass
            except Exception:
                logger.exception("collector loop failed to close gracefully")

        for platform in self._tasks.copy():
            await self._stop_task(platform)

        await self._collect()  # final collection to prevent dropped notifs

        self.loadedProviders.clear()
        self._tasks.clear()
        self._signals.clear()
