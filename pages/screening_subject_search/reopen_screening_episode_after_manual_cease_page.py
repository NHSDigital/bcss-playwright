from playwright.sync_api import Page
from pages.base_page import BasePage


class ReopenScreeningEpisodeAfterManualCeasePage(BasePage):
    """Reopen Screening Episode After Manual Cease Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page

        # Reopen Screening Episode After Manual Cease - page locators
        self.notes_field = self.page.locator("#UI_NOTES_TEXT")
        self.uncease_and_reopen_episode_button = self.page.get_by_role(
            "button", name="uncease and reopen Episode"
        )

    def fill_notes_field(self, note: str) -> None:
        """
        Enter a note into the notes field.
        Args:
            note (str): The note to enter.
        """
        self.notes_field.fill(note)

    def click_uncease_and_reopen_episode_button(self) -> None:
        """Click the 'uncease and reopen Episode' button."""
        self.click(self.uncease_and_reopen_episode_button)
