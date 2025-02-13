from playwright.sync_api import Page


class ContactsList:

    def __init__(self, page: Page):
        self.page = page

        # Main Menu
        self.view_contacts = self.page.get_by_role("link", name="View Contacts")
        self.edit_my_contact_details = self.page.get_by_role("link", name="Edit My Contact Details")
        self.maintain_contacts = self.page.get_by_role("link", name="Maintain Contacts")
        self.my_preference_settings = self.page.get_by_role("link", name="My Preference Settings")
        self.extract_contact_details = self.page.get_by_role("link", name="Extract Contact Details")
        self.resect_and_discard_accredited_endoscopists = self.page.get_by_role(
            "link", name="Resect and Discard Accredited Endoscopists"
        )

    def click_view_contacts(self) -> None:
        self.view_contacts.click()

    def click_edit_my_contact_details(self) -> None:
        self.edit_my_contact_details.click()

    def click_maintain_contacts(self) -> None:
        self.maintain_contacts.click()

    def click_my_preference_settings(self) -> None:
        self.my_preference_settings.click()

    def click_extract_contact_details(self) -> None:
        self.extract_contact_details.click()

    def click_resect_and_discard_accredited_endoscopists(self) -> None:
        self.resect_and_discard_accredited_endoscopists.click()
