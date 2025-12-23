from playwright.sync_api import Page
from pages.base_page import BasePage


class UnceaseAndInitiateOptinEpisodePage(BasePage):
    """Uncease and Initiate Opt-in Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        self.notes_field = self.page.locator("#UI_NOTES_TEXT")
        self.send_a_kit_button = self.page.get_by_role("button", name="Send a kit")

    def enter_notes(self, notes: str) -> None:
        """
        Enter notes into the 'Notes' field.
        Args:
            notes (str): The notes to enter into the field.
        """
        self.notes_field.fill(notes)

    def click_send_a_kit_button(self) -> None:
        """
        Clicks the 'Send a kit' button.
        """
        self.safe_accept_dialog(self.send_a_kit_button)

    def manually_uncease_the_subject(self, action: str) -> None:
        """
        Uncease the subject and take the specified action.
        Args:
            action (str): The action to take after unceasing the subject.
        """
        self.enter_notes(
            f"Auto test scenario: manual unceasing test for age extension to {action}"
        )
        match action:
            case "send a new kit":
                self.click_send_a_kit_button()
