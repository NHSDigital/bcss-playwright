from playwright.sync_api import Page


class ManualCeasePage:
    """This class contains locators to interact with the manual cease page."""

    def __init__(self, page: Page):
        self.page = page
        self.request_cease_button = page.locator("input[name='BTN_REQUEST_CEASE']")
        self.cease_reason_dropdown = page.locator("#A_C_RequestCeaseReason")
        self.notes_textbox = page.get_by_role("textbox", name="Notes (up to 500 char)")
        self.date_confirmed_field = page.get_by_label("Date Confirmed")
        self.confirm_cease_button = page.get_by_role("button", name="Confirm Cease")
        self.save_request_cease_button = page.locator(
            "input[name='BTN_SAVE'][value='Save Request Cease']"
        )
        self.summary_table = page.locator("#screeningSummaryTable")
        self.record_disclaimer_sent_button = page.get_by_role(
            "button", name="Record Disclaimer Letter Sent"
        )
        self.confirm_disclaimer_sent_button = page.get_by_role("button", name="Confirm")
        self.record_return_disclaimer_button = page.get_by_role(
            "button", name="Record Return of Disclaimer Letter"
        )
        self.notes_field = page.get_by_label("Notes")
