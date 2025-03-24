import os

from playwright.sync_api import Page
from utils.user_tools import UserTools
from utils.click_helper import click
from dotenv import load_dotenv


class BcssLoginPage:

    def __init__(self, page: Page):
        self.page = page
        self.page.goto("/")
        self.username = page.get_by_role("textbox", name="Username")
        self.password = page.get_by_role("textbox", name="Password")
        self.submit_button = page.get_by_role("button", name="submit")
        load_dotenv()  # Take environment variables from .env

    def login_as_user(self, username: str) -> None:
        """Logs in to bcss with specified user credentials
        Args:
            username (str) enter a username that exists in users.json
        """
        # Retrieve and enter username from users.json
        user_details = UserTools.retrieve_user(username)
        self.username.fill(user_details["username"])
        # Retrieve and enter password from .env file
        password = os.getenv("BCSS_PASS")
        self.password.fill(password)
        # Click Submit
        click(self.page, self.submit_button)

