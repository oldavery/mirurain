"""Queue state enumerations for Mirurain."""

from enum import IntEnum


class QueueStatus(IntEnum):
    """Lifecycle states for a queued notification.

    Attributes:
        QUEUED: The entry is queued and waiting to be processed.
        COMPLETED: The entry has been completed.
        PROCESSING: The entry is being processed.
        RETRYING: The entry failed and is scheduled to be retried.
        FAILED: The entry failed.
        DROPPED: The entry was dropped.
    """

    QUEUED = 0

    COMPLETED = 1

    PROCESSING = 2

    RETRYING = 3

    FAILED = 4

    DROPPED = 5
