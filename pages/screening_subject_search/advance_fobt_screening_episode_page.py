from datetime import date
from playwright.sync_api import Page, expect, Locator
from pages.base_page import BasePage
import logging
import pytest


class AdvanceFOBTScreeningEpisodePage(BasePage):
    """Advance FOBT Screening Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # Advance FOBT Screening Episode - page locators
        self.suitable_for_endoscopic_test_button = self.page.get_by_role(
            "button", name="Suitable for Endoscopic Test"
        )
        self.calendar_button = self.page.get_by_role("button", name="Calendar")
        self.test_type_dropdown = self.page.locator("#UI_EXT_TEST_TYPE_2233")
        self.test_type_dropdown_2 = self.page.locator("#UI_EXT_TEST_TYPE_4325")
        self.advance_checkbox = self.page.get_by_label(
            "There are some events available which should only be used in exceptional circumstances. If you wish to see them, check this box"
        )
        self.invite_for_diagnostic_test_button = self.page.get_by_role(
            "button", name="Invite for Diagnostic Test >>"
        )
        self.attend_diagnostic_test_button = self.page.get_by_role(
            "button", name="Attend Diagnostic Test"
        )
        self.other_post_investigation_button = self.page.get_by_role(
            "button", name="Other Post-investigation"
        )
        self.record_other_post_investigation_contact_button = self.page.get_by_role(
            "button", name="Record other post-"
        )
        self.enter_diagnostic_test_outcome_button = self.page.get_by_role(
            "button", name="Enter Diagnostic Test Outcome"
        )
        self.handover_into_symptomatic_care_button = self.page.get_by_role(
            "button", name="Handover into Symptomatic Care"
        )
        self.record_diagnosis_date_button = self.page.get_by_role(
            "button", name="Record Diagnosis Date"
        )
        self.record_contact_with_patient_button = self.page.get_by_role(
            "button", name="Record Contact with Patient"
        )
        self.suitable_for_radiological_test_button = self.page.get_by_role(
            "button", name="Suitable for Radiological Test"
        )
        self.decision_not_to_continue_with_diagnostic_test_button = (
            self.page.get_by_role(
                "button", name="Decision not to Continue with Diagnostic Test"
            )
        )
        self.waiting_decision_to_proceed_with_diagnostic_test_button = (
            self.page.get_by_role(
                "button", name="Waiting Decision to Proceed with Diagnostic Test"
            )
        )

    def click_suitable_for_endoscopic_test_button(self) -> None:
        """Click the 'Suitable for Endoscopic Test' button."""
        self.safe_accept_dialog(self.suitable_for_endoscopic_test_button)

    def click_calendar_button(self) -> None:
        """Click the calendar button to open the calendar picker."""
        self.click(self.calendar_button)

    def select_test_type_dropdown_option(self, text: str) -> None:
        """Select the test type from the dropdown."""
        self.test_type_dropdown.select_option(label=text)

    def select_test_type_dropdown_option_2(self, text: str) -> None:
        """Select the test type from the dropdown."""
        self.test_type_dropdown_2.select_option(label=text)

    def click_invite_for_diagnostic_test_button(self) -> None:
        """Click the 'Invite for Diagnostic Test' button."""
        self.safe_accept_dialog(self.invite_for_diagnostic_test_button)

    def click_attend_diagnostic_test_button(self) -> None:
        """Click the 'Attend Diagnostic Test' button."""
        self.click(self.attend_diagnostic_test_button)

    def click_other_post_investigation_button(self) -> None:
        """Click the 'Other Post-investigation' button."""
        self.safe_accept_dialog(self.other_post_investigation_button)

    def get_latest_event_status_cell(self, latest_event_status: str) -> Locator:
        """Get the cell containing the latest event status."""
        return self.page.get_by_role("cell", name=latest_event_status, exact=True)

    def verify_latest_event_status_value(self, latest_event_status: str) -> None:
        """Verify that the latest event status value is visible."""
        logging.info(f"Verifying subject has the status: {latest_event_status}")
        latest_event_status_cell = self.get_latest_event_status_cell(
            latest_event_status
        )
        try:
            expect(latest_event_status_cell).to_be_visible()
            logging.info(f"Subject has the status: {latest_event_status}")
        except Exception:
            pytest.fail(f"Subject does not have the status: {latest_event_status}")

    def click_record_other_post_investigation_contact_button(self) -> None:
        """Click the 'Record other post-investigation contact' button."""
        self.click(self.record_other_post_investigation_contact_button)

    def click_enter_diagnostic_test_outcome_button(self) -> None:
        """Click the 'Enter Diagnostic Test Outcome' button."""
        self.click(self.enter_diagnostic_test_outcome_button)

    def click_handover_into_symptomatic_care_button(self) -> None:
        """Click the 'Handover Into Symptomatic Care' button."""
        self.click(self.handover_into_symptomatic_care_button)

    def click_record_diagnosis_date_button(self) -> None:
        """Click the 'Record Diagnosis Date' button."""
        self.click(self.record_diagnosis_date_button)

    def click_record_contact_with_patient_button(self) -> None:
        """Click the 'Record Contact with Patient' button."""
        self.click(self.record_contact_with_patient_button)

    def check_advance_checkbox(self) -> None:
        """Selects the 'Advance FOBT' checkbox"""
        self.advance_checkbox.check()

    def click_suitable_for_radiological_test_button(self) -> None:
        """Click the 'Suitable for Radiological Test' button."""
        self.safe_accept_dialog(self.suitable_for_radiological_test_button)

    def click_decision_not_to_continue_with_diagnostic_test(self) -> None:
        """Click the 'Decision not to Continue with Diagnostic Test' button."""
        self.safe_accept_dialog(
            self.decision_not_to_continue_with_diagnostic_test_button
        )

    def click_waiting_decision_to_proceed_with_diagnostic_test(self) -> None:
        """Click the 'Waiting Decision to Proceed with Diagnostic Test' button."""
        self.safe_accept_dialog(
            self.waiting_decision_to_proceed_with_diagnostic_test_button
        )

    def select_ct_colonography_and_invite(self) -> None:
        """
        Enters today's date, selects 'CT Colonography' as the diagnostic test type,
        and clicks the 'Invite for Diagnostic Test' button.
        """
        logging.info("[ADVANCE EPISODE] Selecting CT Colonography and inviting for diagnostic test")

        # Step 1: Enter today's date
        today = date.today().strftime("%d/%m/%Y")
        self.page.locator("#UI_APPT_DATE_38").fill(today)
        logging.info(f"[ADVANCE EPISODE] Entered appointment date: {today}")

        # Step 2: Select 'CT Colonography' from dropdown
        self.page.locator("#UI_EXT_TEST_TYPE_38").select_option(label="CT Colonography")
        logging.info("[ADVANCE EPISODE] Selected test type: CT Colonography")

        # Step 3: Click 'Invite for Diagnostic Test'
        invite_button = self.page.get_by_role("button", name="Invite for Diagnostic Test >>")
        self.safe_accept_dialog(invite_button)

        logging.info("[ADVANCE EPISODE] Invite for diagnostic test completed")

    def record_contact_close_episode_no_contact(self) -> None:
        """
        Records contact with the subject and sets the outcome to 'Close Episode - No Contact'.

        Steps:
            - Clicks the 'Record Contact with Patient' button
            - Selects 'To patient' as the direction
            - Fills start time, end time, and duration
            - Enters a note
            - Selects the outcome 'Close Episode - No Contact'
            - Clicks the save button
        """
        logging.info("[CONTACT RECORD] Starting contact recording flow with outcome: Close Episode - No Contact")

        # Step 1: Click 'Record Contact with Patient' button
        self.page.get_by_role("button", name="Record Contact with Patient").click()
        logging.info("[CONTACT RECORD] Navigated to contact recording screen")

        # Step 2: Select 'To patient' from direction dropdown
        self.page.locator("#UI_DIRECTION").select_option(label="To patient")
        logging.info("[CONTACT RECORD] Selected direction: To patient")

        # Step 3: Enter time details
        self.page.locator("#UI_START_TIME").fill("09:00")
        self.page.locator("#UI_END_TIME").fill("09:10")
        self.page.locator("#UI_DURATION").fill("10")
        logging.info("[CONTACT RECORD] Entered time details: 09:00–09:10, duration 10 mins")

        # Step 4: Enter note
        self.page.locator("#UI_COMMENT_ID").fill("automation test note")
        logging.info("[CONTACT RECORD] Entered note: automation test note")

        # Step 5: Select outcome
        self.page.locator("#UI_OUTCOME").select_option(label="Close Episode - No Contact")
        logging.info("[CONTACT RECORD] Selected outcome: Close Episode - No Contact")

        # Step 6: Click save
        self.page.locator("input[name='UI_BUTTON_SAVE']").click()
        logging.info("[CONTACT RECORD] Contact recording flow completed successfully")
