from literals import Provider

from notification_providers.discord import DiscordNotificationProvider


def get_notification_provider(provider: Provider):
    if provider == "discord":
        return DiscordNotificationProvider()

    raise ValueError(f"Unsupported notification provider: {provider}")
