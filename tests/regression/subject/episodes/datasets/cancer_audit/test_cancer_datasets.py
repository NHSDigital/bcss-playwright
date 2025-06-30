import pytest
import logging
from playwright.sync_api import Page
from classes.subject import Subject
from classes.user import User
from pages.base_page import BasePage
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.logout.log_out_page import LogoutPage
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils.oracle.oracle import OracleDB
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.screening_subject_page_searcher import search_subject_episode_by_nhs_number
from utils.user_tools import UserTools


@pytest.mark.wip
@pytest.mark.regression
@pytest.mark.subject_tests
def test_edit_cancer_audit_dataset_data_items(page: Page) -> None:
    """
    Scenario: If not amending a temporary address, no need to validate it

    This test is checking that if a temporary address is not being amended,
    and the subject's postcode is updated.
    That the subject does not have a temporary address added to them.
    """
    criteria = {
        "latest episode status": "open",
        "latest event status": "A345",
    }
    user = User()
    subject = Subject()

    builder = SubjectSelectionQueryBuilder()

    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria, user=user, subject=subject, subjects_to_retrieve=1
    )

    df = OracleDB().execute_query(query, bind_vars)
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"Selected NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_cancer_audit_show_datasets()

    LogoutPage(page).log_out()
