import logging
import pytest
from datetime import datetime
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.datasets.investigation_dataset_page import (
    InvestigationDatasetsPage,
    DrugTypeOptions,
    BowelPreparationQualityOptions,
    ComfortOptions,
    EndoscopyLocationOptions,
    YesNoOptions,
    InsufflationOptions,
    OutcomeAtTimeOfProcedureOptions,
    LateOutcomeOptions,
    FailureReasonsOptions,
    PolypClassificationOptions,
    PolypAccessOptions,
    PolypInterventionModalityOptions,
    PolypInterventionDeviceOptions,
    PolypInterventionExcisionTechniqueOptions,
    PolypTypeOptions,
    SerratedLesionSubTypeOptions,
    PolypExcisionCompleteOptions,
    PolypDysplasiaOptions,
    YesNoUncertainOptions,
    AdenomaSubTypeOptions,
    CompletionProofOptions,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
from pages.logout.log_out_page import LogoutPage
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)
from utils.investigation_dataset import (
    InvestigationDatasetCompletion,
)
from utils.screening_subject_page_searcher import (
    search_subject_episode_by_nhs_number,
)
from utils.user_tools import UserTools
from utils.datasets.investigation_datasets import (
    get_subject_with_investigation_dataset_ready,
    go_from_investigation_dataset_complete_to_a259_status,
    get_subject_with_a99_status,
    go_from_a99_status_to_a259_status,
)

lnpcp_string = "LNPCP"

general_information = {
    "site": -1,
    "practitioner": -1,
    "testing clinician": -1,
    "aspirant endoscopist": None,
}

drug_information = {
    "drug_type1": DrugTypeOptions.MANNITOL,
    "drug_dose1": "3",
}

endoscopy_information = {
    "endoscope inserted": "yes",
    "procedure type": "therapeutic",
    "bowel preparation quality": BowelPreparationQualityOptions.GOOD,
    "comfort during examination": ComfortOptions.NO_DISCOMFORT,
    "comfort during recovery": ComfortOptions.NO_DISCOMFORT,
    "endoscopist defined extent": EndoscopyLocationOptions.DESCENDING_COLON,
    "scope imager used": YesNoOptions.YES,
    "retroverted view": YesNoOptions.NO,
    "start of intubation time": "09:00",
    "start of extubation time": "09:30",
    "end time of procedure": "10:00",
    "scope id": "Autotest",
    "insufflation": InsufflationOptions.AIR,
    "outcome at time of procedure": OutcomeAtTimeOfProcedureOptions.LEAVE_DEPARTMENT,
    "late outcome": LateOutcomeOptions.NO_COMPLICATIONS,
}

failure_information = {
    "failure reasons": FailureReasonsOptions.ADHESION,
}

completion_information = {
    "completion proof": CompletionProofOptions.VIDEO_APPENDIX,
}


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_a(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - A)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    polyp_1_information = {
        "location": EndoscopyLocationOptions.ANUS,
        "classification": PolypClassificationOptions.ISP,
        "estimate of whole polyp size": "20",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.POLYPECTOMY,
        "device": PolypInterventionDeviceOptions.HOT_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.SERRATED_LESION,
        "serrated lesion sub type": SerratedLesionSubTypeOptions.MIXED_POLYP,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "20",
        "polyp dysplasia": PolypDysplasiaOptions.NO_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "20")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_b(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - B)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    polyp_1_information = {
        "location": EndoscopyLocationOptions.RECTUM,
        "classification": PolypClassificationOptions.IS,
        "estimate of whole polyp size": "20",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.EMR,
        "device": PolypInterventionDeviceOptions.HOT_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.ADENOMA,
        "adenoma sub type": AdenomaSubTypeOptions.TUBULOVILLOUS_ADENOMA,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "21",
        "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "21")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_c(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - C)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    polyp_1_information = {
        "location": EndoscopyLocationOptions.SIGMOID_COLON,
        "classification": PolypClassificationOptions.IIA,
        "estimate of whole polyp size": "22",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.ESD,
        "device": PolypInterventionDeviceOptions.ENDOSCOPIC_KNIFE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.ADENOMA,
        "adenoma sub type": AdenomaSubTypeOptions.VILLOUS_ADENOMA,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "22",
        "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.UNCERTAIN,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "22")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_d(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - D)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    polyp_1_information = {
        "location": EndoscopyLocationOptions.DESCENDING_COLON,
        "classification": PolypClassificationOptions.IIB,
        "estimate of whole polyp size": "20",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.POLYPECTOMY,
        "device": PolypInterventionDeviceOptions.COLD_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
        "polyp appears fully resected endoscopically": YesNoOptions.YES,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.ADENOMA,
        "adenoma sub type": AdenomaSubTypeOptions.NOT_REPORTED,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "19",
        "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.UNCERTAIN,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "20")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_e(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - E)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    endoscopy_information["endoscopist defined extent"] = (
        EndoscopyLocationOptions.APPENDIX
    )

    polyp_1_information = {
        "location": EndoscopyLocationOptions.SPLENIC_FLEXURE,
        "classification": PolypClassificationOptions.IIC,
        "estimate of whole polyp size": "19",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.EMR,
        "device": PolypInterventionDeviceOptions.COLD_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
        "polyp appears fully resected endoscopically": YesNoOptions.YES,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.SERRATED_LESION,
        "serrated lesion sub type": SerratedLesionSubTypeOptions.HYPERPLASTIC_POLYP,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "20",
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "20")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_f(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - F)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    endoscopy_information["endoscopist defined extent"] = (
        EndoscopyLocationOptions.APPENDIX
    )

    polyp_1_information = {
        "location": EndoscopyLocationOptions.TRANSVERSE_COLON,
        "classification": PolypClassificationOptions.LST_G,
        "estimate of whole polyp size": "21",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.ESD,
        "device": PolypInterventionDeviceOptions.HOT_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
        "polyp appears fully resected endoscopically": YesNoOptions.YES,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.SERRATED_LESION,
        "serrated lesion sub type": SerratedLesionSubTypeOptions.MIXED_POLYP,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "21",
        "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "21")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_g(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - G)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    endoscopy_information["endoscopist defined extent"] = (
        EndoscopyLocationOptions.APPENDIX
    )

    polyp_1_information = {
        "location": EndoscopyLocationOptions.HEPATIC_FLEXURE,
        "classification": PolypClassificationOptions.LST_NG,
        "estimate of whole polyp size": "18",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.POLYPECTOMY,
        "device": PolypInterventionDeviceOptions.HOT_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.SERRATED_LESION,
        "serrated lesion sub type": SerratedLesionSubTypeOptions.SESSILE_SERRATED_LESION,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "20",
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "20")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_h(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - H)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    endoscopy_information["endoscopist defined extent"] = (
        EndoscopyLocationOptions.APPENDIX
    )

    polyp_1_information = {
        "location": EndoscopyLocationOptions.ASCENDING_COLON,
        "classification": PolypClassificationOptions.IIA,
        "estimate of whole polyp size": "20",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.EMR,
        "device": PolypInterventionDeviceOptions.HOT_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.SERRATED_LESION,
        "serrated lesion sub type": SerratedLesionSubTypeOptions.SESSILE_SERRATED_LESION_WITH_DYSPLASIA,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "22",
        "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "22")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_i(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - I)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    endoscopy_information["endoscopist defined extent"] = (
        EndoscopyLocationOptions.APPENDIX
    )

    polyp_1_information = {
        "location": EndoscopyLocationOptions.CAECUM,
        "classification": PolypClassificationOptions.ISP,
        "estimate of whole polyp size": "21",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.ESD,
        "device": PolypInterventionDeviceOptions.ENDOSCOPIC_KNIFE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.SERRATED_LESION,
        "serrated lesion sub type": SerratedLesionSubTypeOptions.TRADITIONAL_SERRATED_ADENOMA,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "21",
        "polyp dysplasia": PolypDysplasiaOptions.LOW_GRADE_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "21")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_r(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - R)
    """
    df = get_subject_with_investigation_dataset_ready()
    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).click_main_menu_link()
    BasePage(page).go_to_screening_subject_search_page()
    search_subject_episode_by_nhs_number(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    endoscopy_information["endoscopist defined extent"] = (
        EndoscopyLocationOptions.APPENDIX
    )

    polyp_1_information = {
        "location": EndoscopyLocationOptions.TRANSVERSE_COLON,
        "classification": PolypClassificationOptions.IS,
        "estimate of whole polyp size": "19",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.ESD,
        "device": PolypInterventionDeviceOptions.HOT_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
        "polyp appears fully resected endoscopically": YesNoOptions.YES,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.ADENOMA,
        "adenoma sub type": AdenomaSubTypeOptions.TUBULAR_ADENOMA,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "20",
        "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "20")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_lnpcp_from_histology_s(
    page: Page,
) -> None:
    """
    This test identifies an LNPCP result from histology. (BCSS-5568 - S)
    """
    df = get_subject_with_a99_status()

    nhs_no = df.iloc[0]["subject_nhs_number"]
    logging.info(f"NHS Number: {nhs_no}")

    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    go_from_a99_status_to_a259_status(page, nhs_no)

    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    endoscopy_information["endoscopist defined extent"] = (
        EndoscopyLocationOptions.APPENDIX
    )

    polyp_1_information = {
        "location": EndoscopyLocationOptions.SIGMOID_COLON,
        "classification": PolypClassificationOptions.LST_NG,
        "estimate of whole polyp size": "5",
        "polyp access": PolypAccessOptions.EASY,
        "left in situ": YesNoOptions.NO,
    }

    polyp_1_intervention = {
        "modality": PolypInterventionModalityOptions.ESD,
        "device": PolypInterventionDeviceOptions.HOT_SNARE,
        "excised": YesNoOptions.YES,
        "retrieved": YesNoOptions.YES,
        "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
    }

    polyp_1_histology = {
        "date of receipt": datetime.today(),
        "date of reporting": datetime.today(),
        "pathology provider": -1,
        "pathologist": -1,
        "polyp type": PolypTypeOptions.ADENOMA,
        "adenoma sub type": AdenomaSubTypeOptions.VILLOUS_ADENOMA,
        "polyp excision complete": PolypExcisionCompleteOptions.R1,
        "polyp size": "5",
        "polyp dysplasia": PolypDysplasiaOptions.NOT_REPORTED,
        "polyp carcinoma": YesNoUncertainOptions.NO,
    }

    polyp_information = [polyp_1_information]
    polyp_intervention = [polyp_1_intervention]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible("Abnormal")
    go_from_investigation_dataset_complete_to_a259_status(page)
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    polyp_1_information["estimate of whole polyp size"] = "20"
    polyp_1_histology["polyp size"] = "20"

    polyp_information = [polyp_1_information]
    polyp_histology = [polyp_1_histology]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        completion_information=completion_information,
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
    )

    InvestigationDatasetsPage(page).expect_text_to_be_visible(lnpcp_string)
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, "20")
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, lnpcp_string)

    mark_dataset_not_complete_and_assert(page)


def mark_dataset_not_complete_and_assert(page: Page) -> None:
    """
    Marks the investigation dataset as not complete and asserts that the polyp size and category are None.
    """
    logging.info("Marking investigation dataset not complete")
    InvestigationDatasetsPage(page).click_edit_dataset_button()
    InvestigationDatasetsPage(page).check_dataset_incomplete_checkbox()
    InvestigationDatasetsPage(page).click_save_dataset_button()
    InvestigationDatasetsPage(page).assert_polyp_alogrithm_size(1, None)
    InvestigationDatasetsPage(page).assert_polyp_categrory(1, None)
    LogoutPage(page).log_out()
