"""Public package entry points for Mirurain."""

from .app import main


def entrypoint() -> None:
    """Start Mirurain from the installed console script entry point."""
    main()
