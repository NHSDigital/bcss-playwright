import pytest
from pages.base_page import BasePage
from utils.user_tools import UserTools
from datetime import timedelta
from pages.call_and_recall.call_and_recall_page import CallAndRecallPage
from pages.call_and_recall.create_a_plan_page import CreateAPlanPage
from pages.call_and_recall.invitations_monitoring_page import InvitationsMonitoringPage
from pages.call_and_recall.invitations_plans_page import InvitationsPlansPage
from utils.subject_utils import (
    get_active_invitation_plan,
    calculate_subject_shortfall,
    create_subject,
)
from utils.date_time_utils import DateTimeUtils
from utils.subject_utils import get_active_invitation_plan

random_offset = DateTimeUtils.random_offset
from playwright.sync_api import Page

@pytest.fixture
def db_connection():
    """
    Temporary stub for the database connection fixture.
    Replace with actual database session or connection as needed.
    """
    return None  # Or a mock object if needed


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """
    Before every test is executed, this fixture logs in to BCSS as a test user and navigates to the call and recall page
    """
    # Log in to BCSS
    UserTools.user_login(page, "Hub Manager State Registered at BCS01")

    # Go to call and recall page
    BasePage(page).go_to_call_and_recall_page()


@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.call_and_recall
def test_add_subjects_and_create_invitation_plan(
    page: Page, db_connection, general_properties: dict
) -> None:
    """
    # Feature: Create Subjects

    # Narrative Description:
    # As a system administrator,
    # I want add new subjects into the system,
    # so that I have enough subjects to process during the smoke screen tests

    # Scenario: Add new people into the invitation plan, people who will turn 60 in the next 20 months in England
    # screening center "Wolverhampton SC" in hub "Midlands and NW Hub" (England)
    """

    # Given there were less than "28" subjects to invite per day in the active invitation plan for screening center "23162" hub "23159" in region "England"
    sc_code = general_properties["screening_centre_code"]
    hub_code = general_properties["hub_code"]
    region = general_properties["region"]
    daily_target = int(general_properties["daily_invitation_rate"])

    active_plan = get_active_invitation_plan(hub_code, sc_code, db_connection)
    assert active_plan, "No active invitation plan found"
    print(
        f"Active Plan → start: {active_plan.start_date}, end: {active_plan.end_date}, "
        f"per day: {active_plan.invitations_per_day}, due: {active_plan.invitations_due}"
    )

    # When sufficient additional subjects are created so that there are at least "28" subjects to invite per day in the active invitation plan for screening center "23162" hub "23159" in region "England"
    if active_plan.invitations_per_day < daily_target:
        subjects_needed = calculate_subject_shortfall(active_plan, daily_target)
        for _ in range(subjects_needed):
            birth_date = (
                active_plan.start_date
                + timedelta(
                    DateTimeUtils.random_offset(
                        active_plan.start_date, active_plan.end_date
                    )
                )
                - timedelta(days=365 * 60)
            )
            create_subject(
                birth_date=birth_date,
                screening_centre=sc_code,
                hub=hub_code,
                region=region,
            )

    # And a new invitation plan is created if there are less than "28" subjects to invite per day in the active invitation plan for screening centre "23162" "BCS001" hub "23159" in region "England"
    CallAndRecallPage(page).go_to_planning_and_monitoring_page()
    InvitationsMonitoringPage(page).go_to_invitation_plan_page(sc_code)
    InvitationsPlansPage(page).go_to_create_a_plan_page()
    CreateAPlanPage(page).click_set_all_button()
    CreateAPlanPage(page).fill_daily_invitation_rate_field(str(daily_target))
    CreateAPlanPage(page).click_update_button()

    # Then there are at least "28" subjects to invite per day in the active invitation plan for screening center "23162" hub "23159" in region "England"
    expected_weekly_rate = str(daily_target * 5)  # Assuming 5-day weeks
    CreateAPlanPage(page).verify_weekly_invitation_rate_for_weeks(
        1, 50, expected_weekly_rate
    )
