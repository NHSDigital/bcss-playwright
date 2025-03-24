from playwright.sync_api import Page
from utils.click_helper import click

class InvitationsMonitoring:
    def __init__(self, page: Page):
        self.page = page
        # Call and Recall - page links
        self.bcss009_invitations_plan = self.page.get_by_role("link", name="BCS009")
        self.bcss001_invitations_plan = self.page.get_by_role("link", name="BCS001")

    def go_to_bcss009_invitations_plan_page(self):
        click(self.page, self.bcss009_invitations_plan)

    def go_to_bcss001_invitations_plan_page(self):
        click(self.page, self.bcss001_invitations_plan)



