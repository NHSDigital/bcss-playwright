import pytest
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.surveillance.surveillance_page import SurveillancePage
from pages.surveillance.produce_healthcheck_forms_page import (
    ProduceHealthCheckFormsPage,
)
from classes.repositories.subject_repository import SubjectRepository


class GenerateHealthCheckFormsUtil:
    def __init__(self, page: Page):
        self.page = page

    def invite_surveillance_subjects_early(self, screening_centre_id: str) -> str:
        """
        Invite surveillance subjects early by generating health check forms.
        Args:
            screening_centre_id (str): The screening centre id.
        Returns:
            str: The NHS number of the early invite subject.
        """
        BasePage(self.page).go_to_surveillance_page()
        SurveillancePage(self.page).go_to_produce_healthcheck_forms_page()
        ProduceHealthCheckFormsPage(self.page).change_surveillance_due_count_volume(1)
        ProduceHealthCheckFormsPage(self.page).click_recalculate_button()

        surveillance_due_count_date = ProduceHealthCheckFormsPage(
            self.page
        ).return_surveillance_due_count_date_value()
        nhs_no = self.find_early_invite_subjects(screening_centre_id, surveillance_due_count_date)
        ProduceHealthCheckFormsPage(self.page).click_generate_healthcheck_forms_button()
        return nhs_no

    def find_early_invite_subjects(self, screening_centre_id: str, surveillance_due_count_date: str) -> str:
        """
        Find an early invite subject for surveillance based on the surveillance due count date.
        Args:
            surveillance_due_count_date (str): The surveillance due count date.
        Returns:
            str: The NHS number of the early invite subject.
        """
        nhs_no = SubjectRepository().get_early_subject_to_be_invited_for_surveillance(
            screening_centre_id,
            surveillance_due_count_date,
        )
        return nhs_no
