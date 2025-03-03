from playwright.sync_api import Page

class InvitationsPlans:
    def __init__(self, page: Page):
        self.page = page
        # Call and Recall - page links
        self.create_a_plan = self.page.get_by_role("button", name="Create a Plan")

    def go_to_create_a_plan_page(self):
        self.create_a_plan.click()





