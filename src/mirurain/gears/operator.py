"""Developer utilities gear for Mirurain."""

from datetime import UTC, datetime

from humanfriendly import format_number, format_timespan
from humanfriendly.text import dedent
from stoat import SendableEmbed
from stoat.ext import commands
from tortoise.expressions import Q

from mirurain.enums import Platform, QueueStatus
from mirurain.tables import NotificationQueue
from mirurain.utilities.mirurain import MirurainBot


class OperatorGear(commands.Gear):
    """Operator-only commands and helpers for Mirurain."""

    def __init__(self, bot: MirurainBot) -> None:
        """Initialise the gear with the active bot instance."""
        super().__init__()
        self.bot = bot

    @commands.group()
    async def tools(self, _: commands.Context) -> None:
        """Root command group for instance tooling."""

    @tools.group()
    async def notifications(self, ctx: commands.Context) -> None:
        """Command group for interacting with the bot's notification queue."""

    @notifications.command()
    async def overview(self, ctx: commands.Context) -> None:
        """Send a summary of current queue health for operators.

        Args:
            ctx: Command execution context.
        """
        # Get average roundtrip time
        roundtrip_rows = await NotificationQueue.filter(
            status=QueueStatus.COMPLETED
        ).values("created_at", "updated_at")
        if roundtrip_rows:
            roundtrip = format_timespan(
                sum(
                    (row["updated_at"] - row["created_at"]).total_seconds()
                    for row in roundtrip_rows
                )
                / len(roundtrip_rows),
                True,
            )
        else:
            roundtrip = "Unknown"

        # Get queue total
        total_queued = format_number(
            await NotificationQueue.filter(
                Q(status=QueueStatus.QUEUED)
                | Q(status=QueueStatus.RETRYING)
                | Q(status=QueueStatus.PROCESSING)
            ).count()
        )

        # Get recently completed
        recently_completed = format_number(
            await NotificationQueue.filter(
                status=QueueStatus.COMPLETED,
                updated_at__gte=datetime.now(UTC).replace(
                    hour=0,
                    minute=0,
                    second=0,
                    microsecond=0,
                ),
            ).count()
        )

        # Make da embed :3
        embed = SendableEmbed(
            title="Notification Overview",
            description=dedent(f"""
            **Roundtrip:** {roundtrip}
            **Queued:** {total_queued}
            **Completed today:** {recently_completed}
            """),
        )

        await ctx.message.reply(embeds=[embed])

    @notifications.command()
    async def test(self, ctx: commands.Context):
        """Queue a test notification so the queue behaviour can be verified quickly.

        Args:
            ctx: Command execution context.
        """
        await NotificationQueue.create(
            status=QueueStatus.QUEUED,
            embed=await SendableEmbed(
                title="Testing!~",
                description="Mirurain is Stoat's premier social media aggregator made with love by <@01HXFHK4XH3J35QY0ZK4ZZ46G9>!~",
                color="#c1aec6",
            ).to_dict(self.bot.state),
            server_id=ctx.server.id if ctx.server is not None else "dm",
            channel_id=ctx.channel_id,
            source=Platform.NONE,
            source_post_canonical=f"fake:{ctx.message.id}",
            source_author_canonical=f"user:{ctx.author_id}",
        )
        await ctx.message.reply("Queued a fake post notification for this channel.")
