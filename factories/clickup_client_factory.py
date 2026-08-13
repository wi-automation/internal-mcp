from notification_providers.clickup import ClickUpNotificationProvider


def get_clickup_client() -> ClickUpNotificationProvider:
    return ClickUpNotificationProvider()
