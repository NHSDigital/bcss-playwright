from playwright.sync_api import Page

class ArchivedBatchList:
    def __init__(self, page: Page):
        self.page = page
        # Archived Batch List - page filters
        self.id_filter = self.page.locator("#batchIdFilter")
        self.type_filter = self.page.locator("#batchTypeFilter")
        self.original_filter = self.page.locator("#originalBatchIdFilter")
        self.event_code_filter = self.page.locator("#eventCodeFilter")
        self.description_filter = self.page.locator("#eventDescriptionFilter")
        self.batch_split_by_filter = self.page.locator("#splitByFilter")
        self.screening_centre_filter = self.page.locator("#screeningCentreFilter")
        self.count_filter = self.page.locator("#countFilter")

    def enter_id_filter(self, search_text: str):
        self.id_filter.click()
        self.id_filter.fill(search_text)
        self.id_filter.press("Enter")

    def enter_type_filter(self, search_text: str):
        self.type_filter.click()
        self.type_filter.fill(search_text)
        self.type_filter.press("Enter")

    def enter_original_filter(self, search_text: str):
        self.original_filter.click()
        self.original_filter.fill(search_text)
        self.original_filter.press("Enter")

    def enter_event_code_filter(self, search_text: str):
        self.event_code_filter.click()
        self.event_code_filter.fill(search_text)
        self.event_code_filter.press("Enter")

    def enter_description_filter(self, search_text: str):
        self.description_filter.click()
        self.description_filter.fill(search_text)
        self.description_filter.press("Enter")

    def enter_batch_split_by_filter(self, search_text: str):
        self.batch_split_by_filter.click()
        self.batch_split_by_filter.fill(search_text)
        self.batch_split_by_filter.press("Enter")

    def enter_screening_centre_filter(self, search_text: str):
        self.screening_centre_filter.click()
        self.screening_centre_filter.fill(search_text)
        self.screening_centre_filter.press("Enter")

    def enter_count_filter(self, search_text: str):
        self.count_filter.click()
        self.count_filter.fill(search_text)
        self.count_filter.press("Enter")
