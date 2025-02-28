from playwright.sync_api import Page

class InvitationsMonitoring:
    def __init__(self, page: Page):
        self.page = page
        # Call and Recall - page links
        self.bcss009_invitations_plan = self.page.get_by_role("link", name="BCS009")
        self.bcss001_invitations_plan = self.page.get_by_role("link", name="BCS001")
        #self.Create_a_Plan_page = self.page.get_by_role("button", name="Create a Plan")
        #self.Set_all_page = self.page.get_by_role("link", name="Set all")

    def go_to_bcss009_invitations_plan_page(self):
        self.bcss009_invitations_plan.click()

    def go_to_bcss001_invitations_plan_page(self):
        self.bcss001_invitations_plan.click()



