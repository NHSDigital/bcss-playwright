from playwright.sync_api import Page

class ManageActiveBatch:
    def __init__(self, page: Page):
        self.page = page
        # Manage Active Batch - page buttons
        self.prepare_button = self.page.get_by_role("button", name="Prepare Batch")
        self.retrieve_button = self.page.get_by_role("button", name="Retrieve")
        self.confirm_button = self.page.get_by_role("button", name="Confirm Printed")
        # Manage Active Batch - page buttons (text)
        self.prepare_button_text = self.page.locator('text="Prepare Batch"')
        self.retrieve_button_text = self.page.locator('text="Retrieve"')
        self.confirm_button_text = self.page.locator('text="Confirm Printed"')

    def click_prepare_button(self):
        self.prepare_button.click()

    def click_retrieve_button(self):
        self.retrieve_button.click()

    def click_confirm_button(self):
        self.confirm_button.click()
