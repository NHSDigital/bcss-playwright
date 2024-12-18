from os import environ
import pytest
from playwright.sync_api import Page, expect
from pages.login import BcssLoginPage
from pages.bcss_home_page import BcssHomePage
from dotenv import load_dotenv

load_dotenv()
expect.set_options(timeout=30_000)


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    # This will run before every other job and log in to the homepage.
    username = environ.get("BCSS_USERNAME")
    password = environ.get("BCSS_PASSWORD")
    login_page = BcssLoginPage(page)
    login_page.login(username, password)


def test_homepage_sub_menu(page: Page) -> None:
    homepage = BcssHomePage(page)

    # Check the show and hide sub menu works
    homepage.click_sub_menu_link()
    page.screenshot(path="test-results/homepage/sub_menu_screen.png")
    expect(page.get_by_role("link", name="Organisation Parameters")).to_be_visible()
    homepage.click_hide_sub_menu_link()
    page.screenshot(path="test-results/homepage/menu_screen.png")
    expect(page.get_by_role("cell", name="Alerts", exact=True)).to_be_visible()


def test_homepage_select_org(page: Page) -> None:
    homepage = BcssHomePage(page)

    # check the select org link works
    homepage.click_select_org_link()
    page.screenshot(path="test-results/homepage/select_org_screen.png")
    expect(page.locator("form[action*='/changeorg']")).to_contain_text(
        "Choose an Organisation"
    )
    # Check there is at least one entry in the organisation list
    table_locator = page.locator("table#organisations tr")
    row_count = table_locator.count()
    assert row_count > 0
    # Go back to the home page and make sure it loaded
    homepage.click_back_button()
    expect(page.get_by_role("cell", name="Alerts", exact=True)).to_be_visible()


def test_homepage_release_notes(page: Page) -> None:
    homepage = BcssHomePage(page)

    # Click release notes link
    homepage.click_release_notes_link()
    page.screenshot(path="test-results/homepage/release_notes_screen.png")
    expect(page.locator("#page-title")).to_contain_text("Release Notes")


def test_homepage_help(page: Page) -> None:
    homepage = BcssHomePage(page)

    # check the help link works
    with page.expect_popup() as popup_info:
        homepage.click_help_link()
        help_page = popup_info.value
        help_page.screenshot(path="test-results/homepage/help_screen.png")
        expect(
            help_page.get_by_text("Bowel Cancer Screening System Help")
        ).to_be_visible


def test_homepage_user_guide(page: Page) -> None:
    homepage = BcssHomePage(page)

    # check the user guide works
    with page.expect_popup() as popup_info:
        homepage.click_user_guide_link()
        user_guide = popup_info.value
        expect(user_guide.get_by_text("Bowel Cancer Screening System"))


def test_logout(page: Page) -> None:
    homepage = BcssHomePage(page)
    homepage.click_logout()
    page.screenshot(path="test-results/homepage/logout_screen.png")
    expect(page.get_by_role("link", name="Log in"))
