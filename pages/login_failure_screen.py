from playwright.sync_api import Page, expect


class LoginFailureScreen:
    def __init__(self, page: Page):
        self.page = page
        # Login failure message
        self.login_failure_msg = self.page.get_by_role("heading", name="Sorry, BCSS is unavailable")

    def verify_login_failure_screen_is_displayed(self)->None:
        expect(self.login_failure_msg).to_be_visible()
