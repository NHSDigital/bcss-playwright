from playwright.sync_api import Page
from pages.base_page import BasePage


class AlertsPage:
    def __init__(self, page: Page):
        self.page = page
        self.refresh_alerts_link = self.page.get_by_role("link", name="Refresh alerts")

    def click_refresh_alerts(self):
        self.refresh_alerts_link.click()

    def is_refresh_alerts_visible(self, timeout=5000):
        return self.refresh_alerts_link.is_visible(timeout=timeout)


