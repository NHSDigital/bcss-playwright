from playwright.sync_api import Page

class CommunicationsProduction:
    def __init__(self, page: Page):
        self.page = page
        # Communication Production - page links
        self.active_batch_list_page = self.page.get_by_role("link", name="Active Batch List")
        self.archived_batch_list_page = self.page.get_by_role("link", name="Archived Batch List")
        self.letter_library_index_page = self.page.get_by_role("link", name="Letter Library Index")
        self.letter_signatory_page = self.page.get_by_role("link", name="Letter Signatory")
        self.electronic_communication_management_page = self.page.get_by_role("link", name="Electronic Communication Management")


    def go_to_active_batch_list_page(self):
        self.active_batch_list_page.click()

    def go_to_archived_batch_list_page(self):
        self.archived_batch_list_page.click()

    def go_to_letter_library_index_page(self):
        self.letter_library_index_page.click()

    def go_to_letter_signatory_page(self):
        self.letter_signatory_page.click()

    def go_to_electronic_communication_management_page(self):
        self.electronic_communication_management_page.click()
