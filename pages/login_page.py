import os

from playwright.sync_api import Page
from utils.user_tools import UserTools
from dotenv import load_dotenv


class BcssLoginPage:

    def __init__(self, page: Page):
        self.page = page
        self.page.goto("/")
        self.username = page.get_by_role("textbox", name="Username")
        self.password = page.get_by_role("textbox", name="Password")
        self.submit_button = page.get_by_role("button", name="submit")

    def login_as_user_bcss401(self):
        """Logs in to bcss as the test user 'BCSS401'"""
        # Take environment variables from .env
        load_dotenv()
        # Retrieve and enter username from users.json
        user_details = UserTools.retrieve_user("BCSS401")
        self.username.fill(user_details["username"])
        # Retrieve and enter password from .env file
        password = os.getenv("BCSS_PASS")
        self.password.fill(password)
        # Click submit button
        self.submit_button.click()

    def login_as_user_bcss118(self):
        """Logs in to bcss as the test user 'BCSS118'"""
        # Take environment variables from .env
        load_dotenv()
        # Retrieve and enter username from users.json
        user_details = UserTools.retrieve_user("BCSS118")
        self.username.fill(user_details["username"])
        # Retrieve and enter password from .env file
        password = os.getenv("BCSS_PASS")
        self.password.fill(password)
        # Click submit button
        self.submit_button.click()
