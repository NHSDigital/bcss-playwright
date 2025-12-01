from playwright.sync_api import Page
from pages.screening_subject_search.reopen_episode_page import ReopenEpisodePage


class ReopenSurveillanceEpisodePage(ReopenEpisodePage):
    """Reopen Surveillance Episode Page locators, and methods for interacting with the page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
