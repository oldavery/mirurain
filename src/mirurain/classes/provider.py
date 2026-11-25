"""Abstract provider base classes for Mirurain notification sources."""

import asyncio
from abc import ABC, abstractmethod

from stoat import State

from mirurain.enums import Platform
from mirurain.tables import NotificationQueue


class Provider(ABC):
    """Define the interface for notification providers."""

    def __init__(self, state: State, queue: asyncio.Queue[NotificationQueue]) -> None:
        """Initialise the provider with an output queue.

        Args:
            state: Shared bot state.
            queue: Queue that receives emitted notifications.
        """
        self.queue = queue
        self._state = state
        super().__init__()

    @property
    @abstractmethod
    def platform(self) -> Platform:
        """Return the platform handled by this provider."""

    @abstractmethod
    async def run(self, shutdown: asyncio.Event) -> None:
        """Run the provider task until shutdown is requested.

        Implementations must gracefully handle both shutdown signalling and task cancellation.

        Args:
            shutdown: Event set when the provider should stop.
        """
