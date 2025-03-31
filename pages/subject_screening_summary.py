from playwright.sync_api import Page, expect, Locator
from utils.click_helper import click


class SubjectScreeningSummary:
    def __init__(self, page: Page):
        self.page = page
        # Subject Screening Summary - page filters
        self.subject_screening_summary = self.page.get_by_role("cell", name="Subject Screening Summary", exact=True)
        self.latest_event_status = self.page.get_by_role("cell", name="Latest Event Status", exact=True)
        self.subjects_events_notes = self.page.get_by_role("link", name="Subject Events & Notes")
        self.list_episodes = self.page.get_by_role("link", name="List Episodes")
        self.subject_demographics = self.page.get_by_role("link", name="Subject Demographics")
        self.datasets = self.page.get_by_role("link", name="Datasets")
        self.individual_letters = self.page.get_by_role("link", name="Individual Letters")
        self.patient_contacts = self.page.get_by_role("link", name="Patient Contacts")
        self.more = self.page.get_by_role("link", name="more")
        self.change_screening_status = self.page.get_by_label("Change Screening Status")
        self.reason = self.page.get_by_label("Reason", exact=True)
        self.update_subject_data = self.page.get_by_role("button", name="Update Subject Data")
        self.close_fobt_screening_episode = self.page.get_by_role("button", name="Close FOBT Screening Episode")
        self.go_to_a_page_to_advance_the_episode = self.page.get_by_text("go to a page to Advance the")
        self.go_to_a_page_to_close_the_episode = self.page.get_by_text("go to a page to Close the")

    def get_latest_event_status_cell(self, latest_event_status: str)-> Locator:
        return self.page.get_by_role("cell", name=latest_event_status, exact=True)

    def verify_subject_screening_summary(self)-> None:
        expect(self.subject_screening_summary).to_be_visible()

    def verify_latest_event_status_header(self)-> None:
        expect(self.latest_event_status).to_be_visible()

    def verify_latest_event_status_value(self, latest_event_status: str)-> None:
        latest_event_status_cell = self.get_latest_event_status_cell(latest_event_status)
        expect(latest_event_status_cell).to_be_visible()

    def click_subjects_events_notes(self)-> None:
        click(self.page, self.subjects_events_notes)

    def click_list_episodes(self)-> None:
        click(self.page, self.list_episodes)

    def click_subject_demographics(self)-> None:
        click(self.page, self.subject_demographics)

    def click_datasets(self)-> None:
        click(self.page, self.datasets)

    def click_individual_letters(self)-> None:
        click(self.page, self.individual_letters)

    def click_patient_contacts(self)-> None:
        click(self.page, self.patient_contacts)

    def click_more(self)-> None:
        click(self.page, self.more)

    def select_change_screening_status(self)-> None:
        self.change_screening_status.select_option("4007")

    def select_reason(self)-> None:
        self.reason.select_option("11314")

    def click_update_subject_data(self)-> None:
        click(self.page, self.update_subject_data)

    def click_close_fobt_screening_episode(self)-> None:
        click(self.page, self.close_fobt_screening_episode)

    def go_to_a_page_to_advance_the_episode(self)-> None:
        click(self.page, self.go_to_a_page_to_advance_the_episode)

    def go_to_a_page_to_close_the_episode(self)-> None:
        click(self.page, self.go_to_a_page_to_close_the_episode)
