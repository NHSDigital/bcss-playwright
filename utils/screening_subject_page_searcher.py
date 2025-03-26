from pages.navigation_bar_links import NavigationBar
from pages.bcss_home_page import MainMenu
from pages.subject_screening_page import SubjectScreeningPage
from pages.subject_screening_summary import SubjectScreeningSummary
from playwright.sync_api import Page

def verify_subject_event_status_by_nhs_no(page: Page, nhs_no: str, latest_event_status: str):
    NavigationBar(page).click_main_menu_link()
    MainMenu(page).go_to_screening_subject_search_page()
    SubjectScreeningPage(page).click_nhs_number_filter()
    SubjectScreeningPage(page).nhs_number_filter.fill(nhs_no)
    SubjectScreeningPage(page).nhs_number_filter.press("Tab")
    SubjectScreeningPage(page).select_whole_database_search_area()
    SubjectScreeningPage(page).click_search_button()
    SubjectScreeningSummary(page).verify_subject_screening_summary()
    SubjectScreeningSummary(page).verify_latest_event_status_header()
    SubjectScreeningSummary(page).verify_latest_event_status_value(latest_event_status)
