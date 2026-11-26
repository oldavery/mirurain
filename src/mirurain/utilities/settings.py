"""Application configuration handling."""

from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Stoat(BaseModel):
    """Configuration for interacting with Stoat.chat.

    Attributes:
        api_key: Stoat API key.
        is_bot: Whether the account is a bot. Defaults to True.
    """

    api_key: str
    is_bot: bool = True


class Fanner(BaseModel):
    """Configuration for Mirurain's fan-out system.

    Attributes:
        workers: Number of fan-out workers to run. Defaults to 3.
        sleep: Delay in seconds between fan-out poll cycles. Defaults to 5.
        max_retries: Maximum retry attempts before marking an entry as failed.
            Defaults to 3.
    """

    workers: int = 3
    sleep: float = 5
    max_retries: int = 3


class Status(BaseModel):
    """Configuration for status update scheduling.

    Attributes:
        sleep: Delay in seconds between status updates. Defaults to 30.
        messages: Status messages to cycle through.
    """

    sleep: float = 30

    messages: list[str] = [
        "fanning {fanner.queue} notifications",
        "{fanner.recently_completed} notifications sent today",
    ]


class Database(BaseModel):
    """Database connection settings for Mirurain.

    Attributes:
        uri: Connection URI for any Tortoise ORM-compatible SQL backend.
    """

    uri: str


# Provider workers.
class Bluesky(BaseModel):
    """Configuration for Mirurain's Bluesky provider.

    Attributes:
        jetstreams: Jetstream endpoints to try, in priority order.
        instance: Bluesky PDS instance used for API interactions.
        username: Platform account username.
        password: Platform account password.
    """

    jetstreams: list[str] = [
        "wss://jetstream1.us-east.bsky.network",
        "wss://jetstream2.us-east.bsky.network",
        "wss://jetstream1.us-west.bsky.network",
        "wss://jetstream2.us-west.bsky.network",
    ]

    instance: str

    username: str

    password: str


class Mastodon(BaseModel):
    """Configuration for Mirurain's Mastodon provider.

    Attributes:
        instances: Mastodon instance used for API interactions.
        username: Platform account username.
        password: Platform account password.
    """

    instances: str

    username: str

    password: str


class NoStr(BaseModel):
    """Configuration for Mirurain's Nostr provider.

    Attributes:
        relays: Relay URLs to listen to for inbound Nostr events.
    """

    relays: list[str] = [
        "wss://relay.damus.io",
        "wss://nos.lol",
        "wss://relay.nostr.band",
        "wss://relay.snort.social",
        "wss://relay.nostr.info",
    ]


class Tumblr(BaseModel):
    """Configuration for Mirurain's Tumblr provider.

    Attributes:
        oauth_key: Tumblr application API key.
    """

    oauth_key: str  # stupid fucking faggots


class Settings(BaseSettings):
    """Top-level runtime configuration for Mirurain.

    Attributes:
        stoat: Stoat configuration settings.
        database: Database configuration settings.
        bluesky_enabled: Whether the Bluesky provider is enabled.
        bluesky: Optional Bluesky configuration settings.
        mastodon_enabled: Whether the Mastodon provider is enabled.
        mastodon: Optional Mastodon configuration settings.
        nostr_enabled: Whether the Nostr provider is enabled.
        nostr: Optional Nostr configuration settings.
    """

    stoat: Stoat
    database: Database
    fanner: Fanner = Fanner()
    status: Status = Status()
    bluesky_enabled: bool = Field(False, validation_alias="BLUESKY_ENABLED")
    bluesky: Bluesky | None = None
    mastodon_enabled: bool = Field(False, validation_alias="MASTODON_ENABLED")
    mastodon: Mastodon | None = None
    nostr_enabled: bool = Field(False, validation_alias="NOSTR_ENABLED")
    nostr: NoStr | None = None
    tumblr_enabled: bool = Field(False, validation_alias="TUMBLR_ENABLED")
    tumblr: Tumblr | None = None

    model_config = SettingsConfigDict(
        env_prefix="mirurain_",
        env_nested_delimiter="_",
        env_nested_max_split=1,
    )


@lru_cache
def _get_settings() -> Settings:
    """Load environment variables and build a cached settings instance.

    Returns:
        Settings: Cached settings instance.
    """
    load_dotenv()
    return Settings()  # pyright: ignore[reportCallIssue]


settings = _get_settings()
