from pages.base_page import BasePage
from pages.subject_screening_search_page import SubjectScreeningPage, SearchAreaSearchOptions
from pages.subject_screening_summary import SubjectScreeningSummary
from playwright.sync_api import Page


def verify_subject_event_status_by_nhs_no(page: Page, nhs_no: str, latest_event_status: str)->None:
    """
    This is used to check that the latest event status of a subject has been updated to what is expected
    We provide the NHS Number for the subject and the expected latest event status and it navigates to the correct page
    From here it searches for that subject against the whole database and verifies the latest event status is as expected
    """
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    SubjectScreeningPage(page).click_nhs_number_filter()
    SubjectScreeningPage(page).nhs_number_filter.fill(nhs_no)
    SubjectScreeningPage(page).nhs_number_filter.press("Tab")
    SubjectScreeningPage(page).select_search_area_option(SearchAreaSearchOptions.SEARCH_AREA_WHOLE_DATABASE.value)
    SubjectScreeningPage(page).click_search_button()
    SubjectScreeningSummary(page).verify_subject_screening_summary()
    SubjectScreeningSummary(page).verify_latest_event_status_header()
    SubjectScreeningSummary(page).verify_latest_event_status_value(latest_event_status)
