from playwright.sync_api import Page
from pages.base_page import BasePage

class InvitationsMonitoring(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

    def go_to_invitation_plan_page(self, sc_id)->None:
        self.click(self.page.get_by_role("link", name=sc_id))
