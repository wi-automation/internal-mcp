from literals import Provider

from notification_providers.discord import DiscordNotificationProvider
from notification_providers.mattermost import MattermostNotificationProvider


def get_notification_provider(provider: Provider):
    if provider == "discord":
        return DiscordNotificationProvider()

    if provider == "mattermost":
        return MattermostNotificationProvider()

    raise ValueError(f"Unsupported notification provider: {provider}")
