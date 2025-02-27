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
        self.status_filter = self.page.locator("#batchStatusFilter")
        self.count_filter = self.page.locator("#countFilter")
