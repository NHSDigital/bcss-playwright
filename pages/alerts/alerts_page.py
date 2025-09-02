from playwright.sync_api import Page
from pages.base_page import BasePage


class AlertsPage:
    def __init__(self, page: Page):
        self.page = page
        self.refresh_alerts_link = self.page.get_by_role("link", name="Refresh alerts")

    def click_refresh_alerts(self):
        """Clicks the 'Refresh Alerts' link to trigger an update of alert messages."""
        self.refresh_alerts_link.click()

    def is_refresh_alerts_visible(self, timeout=5000):
        """Returns True if the 'Refresh Alerts' link is visible within the given timeout."""
        return self.refresh_alerts_link.is_visible(timeout=timeout)


