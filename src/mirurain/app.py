"""Application bootstrap and command registration for Mirurain."""

from importlib.metadata import version
from time import time

from loguru import logger

from mirurain.events.startup import StartupEvent
from mirurain.gears.fanner import FannerGear
from mirurain.gears.operator import OperatorGear
from mirurain.gears.providers import ProviderGear
from mirurain.gears.status import StatusGear

from .utilities.mirurain import MirurainBot
from .utilities.settings import settings

gears = [FannerGear, OperatorGear, StatusGear, ProviderGear]


def main() -> None:
    """Start Mirurain and register the built-in gears."""
    start = time()
    bot = MirurainBot()

    @bot.listen()
    async def startup(event: StartupEvent) -> None:
        """Register gears once startup dispatches.

        Args:
            event: Startup lifecycle event.
        """
        for g in gears:
            gear = g(bot)
            await bot.add_gear(gear)
            logger.info(f"registered {gear.qualified_name}")
        logger.info("completed registering gears")

        end = time()
        logger.info(f"initialised in {(end - start) * 1000:.2f}ms")

    logger.info(f"starting mirurain v{version('mirurain')}")
    bot.run(settings.stoat.api_key)
