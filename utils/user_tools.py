import json
import logging
import os
from pathlib import Path
from flask.cli import load_dotenv
from playwright.sync_api import Page

from pages.cognito_login_page import CognitoLoginPage

logger = logging.getLogger(__name__)
USERS_FILE = Path(__file__).parent.parent / "users.json"


class UserTools:
    """
    A utility class for retrieving and doing common actions with users.
    """

    @staticmethod
    def user_login(page: Page, username: str) -> None:
        """
        Logs into the BCSS application as a specified user.

        Args:
            page (playwright.sync_api.Page): The Playwright page object to interact with.
            username (str): Enter a username that exists in the users.json file.
        """
        # Load dotenv to enable retrieval of a password from .env file
        load_dotenv()
        # Go to base url
        page.goto("/")
        # Retrieve username from users.json
        user_details = UserTools.retrieve_user(username)
        # Login to bcss using retrieved username and a password stored in the .env file
        CognitoLoginPage(page).login_as_user(user_details["username"], os.getenv("BCSS_PASS"))

    @staticmethod
    def retrieve_user(user: str) -> dict:
        """
        Retrieves the user information as a dict for the user provided.

        Args:
            user (str): The user details required, using the record key from users.json.

        Returns:
            dict: A Python dictionary with the details of the user requested, if present.
        """
        with open(USERS_FILE, 'r') as file:
            user_data = json.loads(file.read())

        if not user in user_data:
            raise UserToolsException(f"User [{user}] is not present in users.json")

        logger.debug(f"Returning user: {user_data[user]}")
        return user_data[user]


class UserToolsException(Exception):
    pass
