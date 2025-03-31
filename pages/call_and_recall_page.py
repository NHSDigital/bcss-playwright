from playwright.sync_api import Page
from utils.click_helper import click


class CallAndRecall:
    def __init__(self, page: Page):
        self.page = page
        # Call and Recall - page links
        self.planning_and_monitoring_page = self.page.get_by_role("link", name="Planning and Monitoring")
        self.generate_invitations_page = self.page.get_by_role("link", name="Generate Invitations")
        self.invitation_generation_progress_page = self.page.get_by_role("link", name="Invitation Generation Progress")
        self.non_invitation_days_page = self.page.get_by_role("link", name="Non Invitation Days")
        self.age_extension_rollout_plans_page = self.page.get_by_role("link", name="Age Extension Rollout Plans")

    def go_to_planning_and_monitoring_page(self)->None:
        click(self.page, self.planning_and_monitoring_page)

    def go_to_generate_invitations_page(self)->None:
        click(self.page, self.generate_invitations_page)

    def go_to_invitation_generation_progress_page(self)->None:
        click(self.page, self.invitation_generation_progress_page)

    def go_to_non_invitation_days_page(self)->None:
        click(self.page, self.non_invitation_days_page)

    def go_to_age_extension_rollout_plans_page(self)->None:
        click(self.page, self.age_extension_rollout_plans_page)
