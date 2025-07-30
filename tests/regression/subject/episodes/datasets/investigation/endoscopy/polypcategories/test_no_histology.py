import logging
import pytest
from datetime import datetime
from playwright.sync_api import Page
from pages.base_page import BasePage
from pages.datasets.investigation_dataset_page import (
    InvestigationDatasetsPage,
    EndoscopyLocationOptions,
    YesNoOptions,
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
    ReasonPathologyLostOptions,
    PolypInterventionSuccessOptions,
    PolypReasonLeftInSituOptions,
)
from pages.datasets.subject_datasets_page import SubjectDatasetsPage
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
    get_default_general_information,
    get_default_drug_information,
    get_default_endoscopy_information,
    complete_and_assert_investigation,
)

lnpcp_string = "LNPCP"
advanced_colorectal_polyp_string = "Advanced colorectal polyp"
other_polyp_string = "Other polyp"
premalignant_polyp_string = "Premalignant polyp"
abnormal_string = "Abnormal"


general_information = get_default_general_information()

drug_information = get_default_drug_information()

endoscopy_information = get_default_endoscopy_information()

failure_information = {
    "failure reasons": FailureReasonsOptions.ADHESION,
}

completion_information = {
    "completion proof": CompletionProofOptions.VIDEO_APPENDIX,
}


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_a(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - A)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.DESCENDING_COLON,
            "classification": PolypClassificationOptions.IIA,
            "estimate of whole polyp size": "20",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.EMR,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.NO,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=lnpcp_string,
        expected_category=lnpcp_string,
        expected_size="20",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_b(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - B)
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
        EndoscopyLocationOptions.CAECUM
    )

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.CAECUM,
            "classification": PolypClassificationOptions.IP,
            "estimate of whole polyp size": "22",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.ESD,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.NO,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=advanced_colorectal_polyp_string,
        expected_size="22",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_c(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - C)
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
        EndoscopyLocationOptions.CAECUM
    )

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.ANUS,
            "classification": PolypClassificationOptions.IIA,
            "estimate of whole polyp size": "21",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.NO,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=other_polyp_string,
        expected_size="21",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_d(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - D)
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
        EndoscopyLocationOptions.CAECUM
    )

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.ASCENDING_COLON,
            "classification": PolypClassificationOptions.ISP,
            "estimate of whole polyp size": "19",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.EMR,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.NO,
            "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
            "polyp appears fully resected endoscopically": YesNoOptions.YES,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=advanced_colorectal_polyp_string,
        expected_size="19",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_e(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - E)
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
        EndoscopyLocationOptions.CAECUM
    )

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.TRANSVERSE_COLON,
            "classification": PolypClassificationOptions.LST_G,
            "estimate of whole polyp size": "9",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.ESD,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.NO,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=premalignant_polyp_string,
        expected_size="9",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_f(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - F)
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
        EndoscopyLocationOptions.CAECUM
    )

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.SIGMOID_COLON,
            "classification": PolypClassificationOptions.IS,
            "estimate of whole polyp size": "21",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        }
    ]

    polyp_1_histology = [
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=lnpcp_string,
        expected_category=lnpcp_string,
        expected_size="21",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_g(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - G)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.ILEUM,
            "classification": PolypClassificationOptions.IP,
            "estimate of whole polyp size": "20",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.ESD,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.YES,
        }
    ]

    polyp_1_histology = [
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=advanced_colorectal_polyp_string,
        expected_size="20",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_h(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - H)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.ANUS,
            "classification": PolypClassificationOptions.IIC,
            "estimate of whole polyp size": "10",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
            "polyp appears fully resected endoscopically": YesNoOptions.YES,
        }
    ]

    polyp_1_histology = [
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=other_polyp_string,
        expected_size="10",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_i(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - I)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.APPENDIX,
            "classification": PolypClassificationOptions.LST_G,
            "estimate of whole polyp size": "18",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.EMR,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
            "polyp appears fully resected endoscopically": YesNoOptions.YES,
        }
    ]

    polyp_1_histology = [
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=advanced_colorectal_polyp_string,
        expected_size="18",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_j(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - J)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.HEPATIC_FLEXURE,
            "classification": PolypClassificationOptions.ISP,
            "estimate of whole polyp size": "8",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        {
            "modality": PolypInterventionModalityOptions.ESD,
            "device": PolypInterventionDeviceOptions.HOT_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        }
    ]

    polyp_1_histology = [
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=premalignant_polyp_string,
        expected_size="8",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_k(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - K)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.SIGMOID_COLON,
            "classification": PolypClassificationOptions.ISP,
            "estimate of whole polyp size": "22",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.POLYPECTOMY,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.NO,
            },
            {
                "modality": PolypInterventionModalityOptions.TISSUE_DESTRUCTION,
                "device": PolypInterventionDeviceOptions.ARGON_BEAM,
            },
        ]
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=lnpcp_string,
        expected_category=lnpcp_string,
        expected_size="22",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_l(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - L)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.ANASTOMOSIS,
            "classification": PolypClassificationOptions.IP,
            "estimate of whole polyp size": "21",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.ESD,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.NO,
            },
            {
                "modality": PolypInterventionModalityOptions.TISSUE_DESTRUCTION,
                "device": PolypInterventionDeviceOptions.ARGON_BEAM,
            },
        ]
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=advanced_colorectal_polyp_string,
        expected_size="21",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_m(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - M)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.ANUS,
            "classification": PolypClassificationOptions.IS,
            "estimate of whole polyp size": "20",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.POLYPECTOMY,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.NO,
            },
            {
                "modality": PolypInterventionModalityOptions.TISSUE_DESTRUCTION,
                "device": PolypInterventionDeviceOptions.ARGON_BEAM,
            },
        ]
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=other_polyp_string,
        expected_size="20",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_n(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - N)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.RECTUM,
            "classification": PolypClassificationOptions.IIA,
            "estimate of whole polyp size": "7",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_1_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.ESD,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.NO,
            },
            {
                "modality": PolypInterventionModalityOptions.BIOPSY,
                "device": PolypInterventionDeviceOptions.COLD_SNARE,
                "intervention success": PolypInterventionSuccessOptions.SUCCESSFUL,
            },
            {
                "modality": PolypInterventionModalityOptions.TISSUE_DESTRUCTION,
                "device": PolypInterventionDeviceOptions.ARGON_BEAM,
            },
        ]
    ]

    polyp_1_histology = [
        {
            "date of receipt": datetime.today(),
            "date of reporting": datetime.today(),
            "pathology provider": -1,
            "pathologist": -1,
            "polyp type": PolypTypeOptions.SERRATED_LESION,
            "serrated lesion sub type": SerratedLesionSubTypeOptions.MIXED_POLYP,
            "polyp dysplasia": PolypDysplasiaOptions.LOW_GRADE_DYSPLASIA,
            "polyp carcinoma": YesNoUncertainOptions.UNCERTAIN,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=premalignant_polyp_string,
        expected_size="7",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_o(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - O)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.SPLENIC_FLEXURE,
            "classification": PolypClassificationOptions.IP,
            "estimate of whole polyp size": "17",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.YES,
            "reason left in situ": PolypReasonLeftInSituOptions.REQUIRES_ANOTHER_PROCEDURE,
        }
    ]

    polyp_1_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.EMR,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
            },
            {
                "modality": PolypInterventionModalityOptions.BIOPSY,
                "device": PolypInterventionDeviceOptions.COLD_SNARE,
                "intervention success": PolypInterventionSuccessOptions.SUCCESSFUL,
            },
        ]
    ]

    polyp_1_histology = [
        {
            "date of receipt": datetime.today(),
            "date of reporting": datetime.today(),
            "pathology provider": -1,
            "pathologist": -1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.VILLOUS_ADENOMA,
            "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
            "polyp carcinoma": YesNoUncertainOptions.UNCERTAIN,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result="Abnormal, procedure incomplete",
        expected_category=None,
        expected_size="17",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_p(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - P)
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

    polyp_1_information = [
        {
            "location": EndoscopyLocationOptions.SPLENIC_FLEXURE,
            "classification": PolypClassificationOptions.IP,
            "estimate of whole polyp size": "12",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.YES,
            "reason left in situ": PolypReasonLeftInSituOptions.CLINICAL_DECISION_NOT_TO_EXCISE,
        }
    ]

    polyp_1_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.EMR,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
            },
            {
                "modality": PolypInterventionModalityOptions.BIOPSY,
                "device": PolypInterventionDeviceOptions.COLD_SNARE,
                "intervention success": PolypInterventionSuccessOptions.SUCCESSFUL,
            },
        ]
    ]

    polyp_1_histology = [
        {
            "date of receipt": datetime.today(),
            "date of reporting": datetime.today(),
            "pathology provider": -1,
            "pathologist": -1,
            "polyp type": PolypTypeOptions.ADENOMA,
            "adenoma sub type": AdenomaSubTypeOptions.VILLOUS_ADENOMA,
            "polyp dysplasia": PolypDysplasiaOptions.HIGH_GRADE_DYSPLASIA,
            "polyp carcinoma": YesNoUncertainOptions.UNCERTAIN,
        }
    ]

    complete_and_assert_investigation(
        page,
        general_information,
        drug_information,
        endoscopy_information,
        failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=None,
        expected_size="12",
        polyp_information=polyp_1_information,
        polyp_intervention=polyp_1_intervention,
        polyp_histology=polyp_1_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_q(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - Q)
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

    polyp_information = [
        {
            "location": EndoscopyLocationOptions.TRANSVERSE_COLON,
            "classification": PolypClassificationOptions.IIC,
            "estimate of whole polyp size": "5",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_intervention = [
        {
            "modality": PolypInterventionModalityOptions.EMR,
            "device": PolypInterventionDeviceOptions.COLD_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.NO,
            "excision technique": PolypInterventionExcisionTechniqueOptions.EN_BLOC,
        }
    ]

    InvestigationDatasetCompletion(page).complete_dataset_with_args(
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        polyp_information=polyp_information,
        completion_information=completion_information,
        polyp_intervention=polyp_intervention,
    )

    try:
        InvestigationDatasetsPage(page).expect_text_to_be_visible(abnormal_string)
        logging.info("Found 'Abnormal' result.")
    except Exception as e:
        logging.error(f"Expected text not found: {e}")
    go_from_investigation_dataset_complete_to_a259_status(page)
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    complete_and_assert_investigation(
        page=page,
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=premalignant_polyp_string,
        expected_size="5",
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_r(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - R)
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

    polyp_information = [
        {
            "location": EndoscopyLocationOptions.ANUS,
            "classification": PolypClassificationOptions.LST_G,
            "estimate of whole polyp size": "6",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_intervention = [
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.COLD_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
        }
    ]

    polyp_histology = [
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        }
    ]

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

    try:
        InvestigationDatasetsPage(page).expect_text_to_be_visible(abnormal_string)
        logging.info("Found 'Abnormal' result.")
    except Exception as e:
        logging.error(f"Expected text not found: {e}")
    go_from_investigation_dataset_complete_to_a259_status(page)
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    complete_and_assert_investigation(
        page=page,
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=other_polyp_string,
        expected_size="6",
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        polyp_histology=polyp_histology,
        completion_information=completion_information,
    )


@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.investigation_dataset_tests
def test_identify_polyp_category_no_histology_s(
    page: Page,
) -> None:
    """
    This test identifies a polyp category where excision was attempted but there is no histology. (BCSS-5109 - S)
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

    polyp_information = [
        {
            "location": EndoscopyLocationOptions.ANUS,
            "classification": PolypClassificationOptions.LST_NG,
            "estimate of whole polyp size": "4",
            "polyp access": PolypAccessOptions.EASY,
            "left in situ": YesNoOptions.NO,
        }
    ]

    polyp_intervention = [
        {
            "modality": PolypInterventionModalityOptions.POLYPECTOMY,
            "device": PolypInterventionDeviceOptions.COLD_SNARE,
            "excised": YesNoOptions.YES,
            "retrieved": YesNoOptions.YES,
            "excision technique": PolypInterventionExcisionTechniqueOptions.PIECE_MEAL,
        }
    ]

    polyp_histology = [
        {
            "pathology lost": YesNoOptions.YES,
            "reason pathology lost": ReasonPathologyLostOptions.LOST_IN_TRANSIT,
        }
    ]

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

    try:
        InvestigationDatasetsPage(page).expect_text_to_be_visible(abnormal_string)
        logging.info("Found 'Abnormal' result.")
    except Exception as e:
        logging.error(f"Expected text not found: {e}")
    go_from_investigation_dataset_complete_to_a259_status(page)
    SubjectScreeningSummaryPage(page).click_datasets_link()
    SubjectDatasetsPage(page).click_investigation_show_datasets()

    polyp_intervention = [
        [
            {
                "modality": PolypInterventionModalityOptions.ESD,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
                "excised": YesNoOptions.NO,
            },
            {
                "modality": PolypInterventionModalityOptions.TISSUE_DESTRUCTION,
                "device": PolypInterventionDeviceOptions.HOT_SNARE,
            },
        ]
    ]

    complete_and_assert_investigation(
        page=page,
        general_information=general_information,
        drug_information=drug_information,
        endoscopy_information=endoscopy_information,
        failure_information=failure_information,
        expected_dataset_result=abnormal_string,
        expected_category=other_polyp_string,
        expected_size="4",
        polyp_information=polyp_information,
        polyp_intervention=polyp_intervention,
        completion_information=completion_information,
    )
