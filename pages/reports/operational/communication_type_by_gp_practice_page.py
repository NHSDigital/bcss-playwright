import logging
from playwright.sync_api import Page, expect


class CommunicationTypeByGpPracticePage:

    def __init__(self, page: Page):
        self.page = page

    def select_screening_centre(self, screening_centre: str) -> None:
        """
        selects a screening centre and verifies the report has been generated

        Args:
            screening_centre (str): the screening centre to use
        """

        self.page.get_by_label("Screening Centre").select_option(screening_centre)
        logging.info(f"{screening_centre} selected")
        expect(self.page.locator("#ntshPageTitle")).to_contain_text(
            "Communication Type for GP Practices"
        )
        expect(self.page.locator("#displayInputParameters")).to_contain_text(
            "Report generated on:"
        )
