import logging
from classes.repositories.subject_repository import SubjectRepository
from pages.base_page import BasePage
from pages.surveillance.surveillance_page import SurveillancePage
from pages.surveillance.produce_healthcheck_forms import ProduceHealthCheckPage
from logging import Logger


def generate_healthcheck_forms(page, general_properties):
    BasePage(page).click_surveillance_link()
    SurveillancePage(page).navigate_to_produce_healthcheck_forms()
    ProduceHealthCheckPage(page).click_on_surveillance_due_count_volume_button()
    ProduceHealthCheckPage(page).fill_volume_in_surveillance_due_count_volume_textbox(1)
    ProduceHealthCheckPage(page).click_on_recalculate_button()
    subject_repo = SubjectRepository()
    screening_centre_id = general_properties["eng_screening_centre_id"]
    s_due_count_date = ProduceHealthCheckPage(page).get_surveillance_due_count_date()
    nhs_number = subject_repo.get_early_subject_to_be_invited_for_surveillance(
        screening_centre_id, s_due_count_date
    )
    assert nhs_number is not None
    logging.info(f"Early subject NHS number: {nhs_number}")
    ProduceHealthCheckPage(page).click_on_generate_healthcheck_forms_button()
    return nhs_number
