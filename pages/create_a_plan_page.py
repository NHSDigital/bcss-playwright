from playwright.sync_api import Page

class CreateAPlan:
    def __init__(self, page: Page):
        self.page = page
        # Call and Recall - page links
        self.set_all_button = self.page.get_by_role("link", name="Set all")
        self.daily_invitation_rate_field = self.page.get_by_placeholder("Enter daily invitation rate")
        self.weekly_invitation_rate_field = self.page.get_by_placeholder("Enter weekly invitation rate")
        self.update_button = self.page.get_by_role("button", name="Update")
        self.confirm_button = self.page.get_by_role("button", name="Confirm")
        self.save_button = self.page.get_by_role("button", name="Save")
        self.note_field = self.page.get_by_placeholder("Enter note")
        self.saveNote_button = self.page.locator("#saveNote").get_by_role("button", name="Save")

    def click_set_all_button(self):
        self.set_all_button.click()

    def fill_daily_invitation_rate_field(self,value):
        self.daily_invitation_rate_field.fill(value)

    def fill_weekly_invitation_rate_field(self,value):
        self.weekly_invitation_rate_field.fill(value)

    def click_update_button(self):
        self.update_button.click()

    def click_confirm_button(self):
        self.confirm_button.click()

    def click_save_button(self):
        self.save_button.click()

    def fill_note_field(self,value):
        self.note_field.fill(value)

    def click_saveNote_button(self):
        self.saveNote_button.click()



