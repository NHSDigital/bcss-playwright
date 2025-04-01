from playwright.sync_api import Page
from pages.base_page import BasePage

class ContactsListPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
        # ContactsList Page
        self.view_contacts_page = self.page.get_by_role("link", name="View Contacts")
        self.edit_my_contact_details_page = self.page.get_by_role("link", name="Edit My Contact Details")
        self.maintain_contacts_page = self.page.get_by_role("link", name="Maintain Contacts")
        self.my_preference_settings_page = self.page.get_by_role("link", name="My Preference Settings")

    def go_to_view_contacts_page(self)->None:
        self.click(self.view_contacts_page)

    def go_to_edit_my_contact_details_page(self)->None:
        self.click(self.edit_my_contact_details_page)

    def go_to_maintain_contacts_details_page(self)->None:
        self.click(self.maintain_contacts_page)

    def go_to_my_preference_settings_page(self)->None:
        self.click(self.my_preference_settings_page)
