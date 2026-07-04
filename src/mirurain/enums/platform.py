"""Platform identifiers used by Mirurain."""

from enum import StrEnum


class Platform(StrEnum):
    """Canonical source platform names for queue records.

    Attributes:
        BLUESKY: Bluesky platform identifier.
        MASTODON: Mastodon platform identifier.
        NOSTR: Nostr platform identifier.
        TUMBLR: Tumblr platform identifier.
        TWITTER: Twitter platform identifier.
    """

    BLUESKY = "bluesky"

    MASTODON = "mastodon"

    NOSTR = "nostr"

    TUMBLR = "tumblr"

    TWITTER = "twitter"

    NONE = "none"
