from playwright.sync_api import Page


def __init__(self, page: Page):
    self.page = page
    # Downloads Page
    self.fit_rollout_summary_page = self.page.get_by_role("link", name="FIT Rollout Summary")
    self.log_devices_page = self.page.get_by_role("link", name="Log Devices")
    self.view_fit_kit_result_page = self.page.get_by_role("link", name="View FIT Kit Result")
    self.kit_service_management_page = self.page.get_by_role("link", name="Kit Service Management")
    self.kit_result_audit_page = self.page.get_by_role("link", name="Kit Result Audit")
    self.view_algorithm_page = self.page.get_by_role("link", name="View Algorithm")
    self.view_screening_centre_fit_page = self.page.get_by_role("link", name="View Screening Centre FIT")
    self.screening_incidents_list_page = self.page.get_by_role("link", name="Screening Incidents List")
    self.manage_qc_products_page = self.page.get_by_role("link", name="Manage QC Products")
    self.maintain_analysers_page = self.page.get_by_role("link", name="Maintain Analysers")
    self.fit_device_id=self.page.get_by_role("textbox", name="FIT Device ID")



def go_to_fit_rollout_summary_page(self):
    self.fit_rollout_summary_page.click()


def go_to_log_devices_page(self):
    self.log_in_page.click()


def go_to_view_fit_kit_result(self):
    self.view_fit_kit_result_page.click()


def go_to_kit_service_management(self):
    self.kit_service_management_page.click()


def go_to_kit_result_audit(self):
    self.kit_result_audit_page.click()


def go_to_view_algorithm(self):
    self.view_algorithm_page.click()


def go_to_view_screening_centre_fit(self):
    self.view_screening_centre_fit_page.click()


def go_to_screening_incidents_list(self):
    self.screening_incidents_list_page.click()


def go_to_manage_qc_products(self):
    self.manage_qc_products_page.click()


def go_to_maintain_analysers(self):
    self.maintain_analysers_page.click()

def go_to_fit_device_id(self):
        self.fit_device_id.enter()


