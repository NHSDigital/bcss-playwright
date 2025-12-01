from playwright.sync_api import Page
from pages.base_page import BasePage


class ProduceHealthCheckPage(BasePage):
    """Page object for navigating to and interacting with the Produce Healthcheck Forms section."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Locators
        self.surveillance_due_count_volume = self.page.locator(
            'input[name="btnChangeVolume"]'
        )
        self.surveillance_due_count_volume_textbox = self.page.locator('[name="txtVolume"]')
        self.recalculate_button = self.page.locator('[name="btnRecalc"]')
        self.surveillance_due_count_date = self.page.locator('[name="txtDueDateTo"]')
        self.health_check_forms=self.page.get_by_role('button', name='Generate HealthCheck Forms')

    def click_on_surveillance_due_count_volume_button(self):
        """Clicks on the Surveillance Due Count Volume Change button."""
        self.click(self.surveillance_due_count_volume)

    def fill_volume_in_surveillance_due_count_volume_textbox(self, volume: int):
        """Enters a volume in the Surveillance Due Count Volume textbox.

        Args:
            volume (str): The volume to enter in the textbox.
        """
        self.surveillance_due_count_volume_textbox.fill(str(volume))
    def click_on_recalculate_button(self):
        """Clicks on the Recalculate button."""
        self.click(self.recalculate_button)

    def get_surveillance_due_count_date(self):
        """Gets the value from the Surveillance Due Count Date textbox.
        """
        return self.surveillance_due_count_date.input_value()

    def click_on_generate_healthcheck_forms_button(self):
        """Clicks on the Generate HealthCheck Forms button."""
        self.safe_accept_dialog(self.health_check_forms)
