from playwright.sync_api import Page
from utils.click_helper import click


class InvitationsMonitoring:
    def __init__(self, page: Page):
        self.page = page

    def go_to_invitation_plan_page(self, sc_id):
        self.page.get_by_role("link", name=sc_id).click()
