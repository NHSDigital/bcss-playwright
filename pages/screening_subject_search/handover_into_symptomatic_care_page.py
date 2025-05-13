from playwright.sync_api import Page
from datetime import datetime

class HandoverIntoSymptomaticCarePage:
    def __init__(self, page: Page):
        self.page = page
        self.referral_dropdown = self.page.get_by_label("Referral")
        self.calendar_button = self.page.get_by_role("button", name="Calendar")
        self.consultant_link = self.page.locator("#UI_NS_CONSULTANT_PIO_SELECT_LINK")
        self.consultant_option = lambda value: self.page.locator(f'[value="{value}"]:visible')
        self.notes_textbox = self.page.get_by_role("textbox", name="Notes")
        self.save_button = self.page.get_by_role("button", name="Save")

    def select_referral_dropdown_option(self, value: str):
        self.referral_dropdown.select_option(value)

    def click_calendar_button(self) -> None:
        self.click(self.calendar_button)

    def select_consultant(self, value: str):
        self.consultant_link.click()
        option = self.consultant_option(value)
        option.wait_for(state="visible")
        option.click()

    def fill_notes(self, notes: str):
        self.notes_textbox.click()
        self.notes_textbox.fill(notes)

    def click_save_button(self):
        self.page.once("dialog", lambda dialog: dialog.accept())
        self.click(self.save_button)

