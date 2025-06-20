import json
import os
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import Page
from pages.login.cognito_login_page import CognitoLoginPage

logger = logging.getLogger(__name__)
USERS_FILE = Path(os.getcwd()) / "users.json"


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
        logging.info(f"Logging in as {username}")
        # Go to base url
        page.goto("/")
        # Retrieve username from users.json
        user_details = UserTools.retrieve_user(username)
        # Login to bcss using retrieved username and a password stored in the .env file
        password = os.getenv("BCSS_PASS")
        if password is None:
            raise ValueError("Environment variable 'BCSS_PASS' is not set")
        CognitoLoginPage(page).login_as_user(user_details["username"], password)

    @staticmethod
    def get_subject_with_criteria(episode_type, episode_status, has_referral_date, has_diagnosis_date, diagnosis_date_reason):
        # Example implementation: fetch NHS number from a test data file based on criteria
        test_data_file = Path(os.getcwd()) / "test_subjects.json"
        if not test_data_file.exists():
            # Fallback to dummy NHS number if file does not exist
            return "1234567890"
        with open(test_data_file, "r") as file:
            subjects = json.load(file)
        for subject in subjects:
            if (
                subject.get("episode_type") == episode_type and
                subject.get("episode_status") == episode_status and
                subject.get("has_referral_date") == has_referral_date and
                subject.get("has_diagnosis_date") == has_diagnosis_date and
                subject.get("diagnosis_date_reason") == diagnosis_date_reason
            ):
                return subject.get("nhs_number", "1234567890")
        # If no match found, then exception is raised
        raise SubjectNotFoundError("No NHS number found using the provided criteria.")

    @staticmethod
    def retrieve_user(user: str) -> dict:
        """
        Retrieves the user information as a dict for the user provided.

        Args:
            user (str): The user details required, using the record key from users.json.

        Returns:
            dict: A Python dictionary with the details of the user requested, if present.
        """
        with open(USERS_FILE, "r") as file:
            user_data = json.loads(file.read())

        if user not in user_data:
            raise UserToolsException(f"User [{user}] is not present in users.json")

        logger.debug(f"Returning user: {user_data[user]}")
        return user_data[user]


class UserToolsException(Exception):
    pass

class SubjectNotFoundError(Exception):
    """Raised when no subject matches the provided criteria."""
    pass
