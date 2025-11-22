"""VIDYA AI microservice package."""

from importlib import metadata


def get_version() -> str:
    """Return the installed package version or fallback."""
    try:
        return metadata.version("vidya_ai_microservice")
    except metadata.PackageNotFoundError:
        return "0.1.0-dev"


__all__ = ["get_version"]
