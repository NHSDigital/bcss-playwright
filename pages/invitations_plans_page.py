from playwright.sync_api import Page
from pages.base_page import BasePage

class InvitationsPlans(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Call and Recall - page links
        self.create_a_plan = self.page.get_by_role("button", name="Create a Plan")
        self.invitations_plans_title = self.page.locator('#page-title:has-text("Invitation Plans")')

    def go_to_create_a_plan_page(self)->None:
        self.click(self.create_a_plan)
