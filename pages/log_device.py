from playwright.sync_api import Page


class LogDevice:

    def __init__(self, page: Page):
        self.page = page
        # Downloads Page
        self.sample_date = self.page.locator("#sampleDate")
        self.save_and_log_device = page.get_by_role("button", name="Save and Log Device")
        self.device_spoilt = page.get_by_role("button", name="Device Spoilt")
        self.spoilt_reason = page.get_by_label("Spoil reason drop down")
        self.log_spoilt = page.get_by_role("button", name="Log as Spoilt")

    def sample_date(self, date: str):
        self.sample_date.click()
        self.sample_date.fill(date)
        self.sample_date.press("Enter")

    def save_and_log_device(self):
        self.save_and_log_device.click()

    def device_spoilt(self):
        self.device_spoilt.click()

    def spoilt_reason(self,value):
        self.device_spoilt.select_option(value)
        self.device_spoilt.click()

    def log_spoilt(self):
        self.log_spoilt.click()
