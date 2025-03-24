import pytest
from playwright.sync_api import Page
from pages import (login_page as login, bcss_home_page as bcss_home, navigation_bar_links as nav_bar_links, log_out_page as logout,
                   login_failure_screen as login_failure)
from utils.oracle import OracleDB

@pytest.fixture(scope="function", autouse=True)
def before_test(page: Page):
    """
    This fixture confirms that users can log in successfully in to BCSS whilst the approved users list is empty
    """
    # Log in to BCSS as bcss401 user, then log out
    login.BcssLoginPage(page).login_as_user("BCSS401")
    bcss_home.BcssHomePage(page).bowel_cancer_screening_system_header_is_displayed()
    nav_bar_links.NavigationBar(page).click_log_out_link()
    logout.Logout(page).verify_log_out_page()
    # Log in to BCSS as bcss118 user, then log out
    login.BcssLoginPage(page).login_as_user("BCSS118")
    bcss_home.BcssHomePage(page).bowel_cancer_screening_system_header_is_displayed()
    nav_bar_links.NavigationBar(page).click_log_out_link()
    logout.Logout(page).verify_log_out_page()

    yield
    OracleDB().delete_all_users_from_approved_users_table()

# @pytest.mark.smoke
def test_only_users_on_approved_can_login_to_bcss(page: Page) -> None:
    # Add bcss401 user to approved users list table
    OracleDB().populate_ui_approved_users_table("BCSS401")
    # BCSS401 user successfully logs in to BCSS whilst on the approved list
    login.BcssLoginPage(page).login_as_user("BCSS401")
    bcss_home.BcssHomePage(page).bowel_cancer_screening_system_header_is_displayed()
    # BCSS401 user logs out
    nav_bar_links.NavigationBar(page).click_log_out_link()
    logout.Logout(page).verify_log_out_page()

    # BCSS118 user fails to logs in to BCSS as they are not on the approved list
    login.BcssLoginPage(page).login_as_user("BCSS118")
    # Verify relevant error message is displayed
    login_failure.LoginFailureScreen(page).verify_login_failure_screen_is_displayed()
    page.close()
    # Delete all users from approved users list table
    # Delete function is called with the yield command in the fixture to make sure it clears the table even when the test fails
