from playwright.sync_api import Page,expect

class Logout:
    def __init__(self, page: Page):
        self.page = page
        # Call and Recall - page links
        self.log_out_msg = self.page.get_by_role("heading", name="You have logged out")

    def verify_log_out_page(self):
        expect(self.log_out_msg).to_be_visible()





