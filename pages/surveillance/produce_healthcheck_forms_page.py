from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class ProduceHealthCheckFormsPage(BasePage):
    """Page object for navigating to and interacting with the Produce Healthcheck Forms page."""

    def __init__(self, page: Page):
        super().__init__(page)

        # Locators
        self.change_surveillance_due_count_volume_button = self.page.locator(
            'input[name="btnChangeVolume"]'
        )
        self.surveillance_due_count_volume_textbox = self.page.locator(
            '[name="txtVolume"]'
        )
        self.generate_healthcheck_forms_button = self.page.get_by_role(
            "button", name="Generate Healthcheck Forms"
        )
        self.recalculate_button = self.page.get_by_role("button", name="Recalculate")
        self.success_message_th = self.page.locator(
            "#displayErrMessage > tbody > tr > th"
        )
        self.surveillance_due_count_date_input = self.page.locator('[name="txtDueDateTo"]')

    def change_surveillance_due_count_volume(self, volume: int) -> None:
        """
        Change the Surveillance Due Count Volume.
        Args:
            volume (int): The new volume to set.
        """
        self.click(self.change_surveillance_due_count_volume_button)
        self.surveillance_due_count_volume_textbox.fill(str(volume))

    def return_surveillance_due_count_date_value(self) -> str:
        """
        Return the Surveillance Due Count Date value from the hidden input.
        Returns:
            str: The Surveillance Due Count Date value.
        """
        return self.surveillance_due_count_date_input.input_value()

    def click_generate_healthcheck_forms_button(self) -> None:
        """Click the Generate Healthcheck Forms button."""
        self.safe_accept_dialog(self.generate_healthcheck_forms_button)
        self.wait_for_success_message()

    def click_recalculate_button(self) -> None:
        """Click the Recalculate button."""
        self.click(self.recalculate_button)

    def wait_for_success_message(self, timeout: float = 5000) -> None:
        """
        Waits for the success message to appear with the expected text.
        Args:
            timeout (float): Maximum time to wait in milliseconds.
        """
        self.success_message_th.wait_for(state="visible", timeout=timeout)
        expect(self.success_message_th).to_have_text(
            "The action was performed successfully"
        )
