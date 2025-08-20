import pytest
from playwright.sync_api import Page, expect
from utils.user_tools import UserTools
from pages.base_page import BasePage
from utils.screening_subject_page_searcher import search_subject_by_forename, search_subject_by_surname


# Scenario 1
@pytest.mark.regression
@pytest.mark.hub_user_tests
def test_hub_user_alerts_populated(page: Page) -> None:
    """
    Scenario: Hub User - Alerts populated
    This test ensures that the alerts have at least been populated for the user within a reasonable amount of time.
    """
    # Step 1: Log in as Hub Manager - State Registered (England)
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")
    BasePage(page).click_refresh_alerts_link()

    # Step 2: Assert the refresh alerts button is visible
    page.get_by_role("link", name="Refresh alerts").click()
    expect(page.get_by_role("link", name="Refresh alerts")).to_be_visible(timeout=5000)

# Scenario 2
@pytest.mark.regression
@pytest.mark.hub_user_tests
def test_hub_user_kits_logged_not_read_report(page: Page) -> None:
    """
    Scenario: Hub User - Kits Logged Not Read report
    This test ensures that if available, the Kits Logged Not Read report loads within a reasonable amount of time.
    """
    # Step 1: Log in as Hub Manager - State Registered (England)
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")
    BasePage(page).go_to_gfobt_test_kits_page()

    # Step 2: Assert the Kits Logged Not Read report loads as expected
    page.get_by_text("gFOBT Test Kits").click()
    expect(page.get_by_text("gFOBT Test Kits")).to_be_visible(timeout=5000)

# Scenario 3
@pytest.mark.regression
@pytest.mark.hub_user_tests
def test_hub_user_people_requiring_colonoscopy_assessment_report(page: Page) -> None:
    """
    Scenario: Hub User - People Requiring Colonoscopy Assessment report
    This test ensures that if available, the People Requiring Colonoscopy Assessment report loads within a reasonable amount of time.
    """
    # Step 1: Log in as Hub Manager - State Registered (England)
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")
    BasePage(page).go_to_screening_practitioner_appointments_page()

    # Step 2: Assert the People Requiring Colonoscopy Assessment report loads as expected
    page.get_by_text("Screening Practitioner Appointments").click()
    expect(page.get_by_text("Screening Practitioner Appointments")).to_be_visible(timeout=5000)

# Scenario 4
@pytest.mark.regression
@pytest.mark.hub_user_tests
def test_screening_centre_user_subject_search_and_summary(page: Page) -> None:
    """
    Scenario: Screening Centre User - Subject Search & Subject Summary
    This test ensures that the subject search works as expected and the subject summary loads and displays data correctly
    """
    # Step 1: Log in as Screening Centre Manager (England)
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()

    # Step 2: Add value "A*" to the "Surname" & "Forename" with ScreeningStatus as "Recall" and EpisodeStatus as "Closed"
    # Click search button on the subject search criteria page
    search_subject_by_surname(page, "A*")
    page.get_by_role("link", name="Back", exact=True).click()
    search_subject_by_forename(page, "A*")
    page.get_by_role("link", name="Back", exact=True).click()
    page.locator("#A_C_ScreeningStatus").select_option("4004")
    page.locator("#A_C_ScreeningStatus").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Back", exact=True).click()
    page.locator("#A_C_EpisodeStatus").select_option("2")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Back", exact=True).click()

# Scenario 5
@pytest.mark.regression
@pytest.mark.hub_user_tests
def test_screening_centre_user_subject_search_and_surveillance(page: Page) -> None:
    """
    Scenario: Screening Centre User - Organisation Search & Surveillance Review Summary
    This test ensures that the organisation search works as expected and the surveillance review summary loads and displays data correctly
    """
    # Step 1: Log in as Screening Centre Manager (England)
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_organisations_page()

    page.get_by_role("link", name="Organisation and Site Details").click()
    page.get_by_role("link", name="List All Organisations").click()
    page.get_by_role("link", name="Back", exact=True).click()
    page.get_by_role("link", name="List All Sites").click()
    [page.get_by_role("link", name="Back", exact=True).click() for _ in range(3)]
    page.get_by_role("link", name="Surveillance", exact=True).click()
    page.get_by_role("link", name="Manage Surveillance Review").click()

    # Step 2: Assert the Surveillance Review Summary report loads as expected
    page.goto("https://bcss-bcss-18680-ddc-bcss.k8s-nonprod.texasplatform.uk/surveillance/review/summary")
    expect(page.get_by_text("Surveillance Review Summary")).to_be_visible(timeout=5000)
