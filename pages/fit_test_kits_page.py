from playwright.sync_api import Page
from utils.click_helper import click


class FITTestKits:
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
        click(self.page, self.fit_rollout_summary_page)

    def go_to_log_devices_page(self):
        click(self.page, self.log_devices_page)

    def go_to_view_fit_kit_result(self):
        click(self.page, self.view_fit_kit_result_page)

    def go_to_kit_service_management(self):
        click(self.page, self.kit_service_management_page)

    def go_to_kit_result_audit(self):
        click(self.page, self.kit_result_audit_page)

    def go_to_view_algorithm(self):
        click(self.page, self.view_algorithm_page)

    def go_to_view_screening_centre_fit(self):
        click(self.page, self.view_screening_centre_fit_page)

    def go_to_screening_incidents_list(self):
        click(self.page, self.screening_incidents_list_page)

    def go_to_manage_qc_products(self):
        click(self.page, self.manage_qc_products_page)

    def go_to_maintain_analysers(self):
        click(self.page, self.maintain_analysers_page)

    def go_to_fit_device_id(self):
            self.fit_device_id.enter()
