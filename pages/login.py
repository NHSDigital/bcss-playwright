import logging
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class BcssLoginPage:

    def __init__(self, page: Page):
        self.page = page
        self.page.goto("/")
        self.username = page.get_by_role("textbox", name="Username")
        self.password = page.get_by_role("textbox", name="Password")
        self.submit_button = page.get_by_role("button", name="submit")

    def login(self, username: str | None, password: str | None) -> None:
        if username is None or password is None:
            logging.error("BCSS_USERNAME and BCSS_PASSWORD environmental variables must be set")
            raise ValueError("BCSS_USERNAME and BCSS_PASSWORD environmental variables must be set")
        self.username.fill(username)
        self.password.fill(password)
        self.submit_button.click()
