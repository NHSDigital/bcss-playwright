from playwright.sync_api import Page
from pages.screening_subject_search.result_from_symptomatic_procedure_page import (
    ResultFromSymptomaticProcedurePage,
)


class HighRiskFindingsResultFromSymptomaticProcedure(
    ResultFromSymptomaticProcedurePage
):
    """High-Risk Findings specific implementation of Result from Symptomatic Procedure Page."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.page = page
