import pytest
import logging
from datetime import datetime
from playwright.sync_api import Page
from utils.oracle.subject_creation_util import CreateSubjectSteps
from utils.sspi_change_steps import SSPIChangeSteps
from utils.user_tools import UserTools
from utils.subject_assertion import subject_assertion
from utils.call_and_recall_utils import CallAndRecallUtils
from utils import screening_subject_page_searcher
from utils.batch_processing import batch_processing
from utils.fit_kit import FitKitLogged, FitKitGeneration
from pages.screening_subject_search.subject_screening_summary_page import (
    SubjectScreeningSummaryPage,
)

# from pages.screening_subject_search.close_fobt_screening_episode_page import (
#     CloseFobtScreeningEpisodePage,
# )
from utils.appointments import book_appointments
from pages.logout.log_out_page import LogoutPage
from pages.base_page import BasePage
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from pages.screening_practitioner_appointments.appointment_detail_page import (
    AppointmentDetailPage,
    ReasonForCancellationOptions,
)
from pages.screening_subject_search.advance_fobt_screening_episode_page import (
    AdvanceFOBTScreeningEpisodePage,
)
from pages.screening_subject_search.record_diagnosis_date_page import (
    RecordDiagnosisDatePage,
)


@pytest.mark.wip
@pytest.mark.usefixtures("setup_org_and_appointments")
@pytest.mark.vpn_required
@pytest.mark.regression
@pytest.mark.fobt_regression_tests
def test_scenario_5(page: Page) -> None:
    """
    Scenario: 5: DNA colonoscopy assessment twice

    S1-S9-S10-S43-A8-A183-A25-J11-J27-A184-A26-A185-A37-A166-P202-(A50)-(A167)-A166-C203 [SSCL4a(A166)]

    This scenario tests where the patient is discharged from their FOBT episode because they DNA their colonoscopy assessment appointment twice. It also tests the diagnosis date and kit result letter spur events.

    Scenario summary:

    > Create a new subject in the FOBT age range > Inactive
    > Run the FOBT failsafe trawl > Call
    > Run the database transition to invite them for FOBT screening > S1(1.1)
    > Process S1 letter batch > S9 (1.1)
    > Run timed events > creates S9 letter (1.1)
    > Process S9 letter batch > S10 (1.1)
    > Log kit > S43 (1.2)
    > Read kit with ABNORMAL result > A8 (1.3)
    > Invite for colonoscopy assessment > A183 (1.11)
    > Process A183 appointment letter > A25 (1.11)
    > Patient DNA appointment > J11 (1.11)
    > Process J11 letter batch > J27 (1.11)
    > Rebook colonoscopy assessment > A184 (1.11)
    > Process A184 letter > A26 (1.11)
    > Patient DNA appointment > A185 (1.11)
    > Process A185 letter batch > A37 (1.11)
    > Process A37 letter batch > A166 (1.11) > P202
    > Record diagnosis date (A50)
    > Process A183 result letter (A167) > A166 (1.11) > C203 (1.13)
    > Check recall [SSCL4a(A166)]
    """

    summary_page = SubjectScreeningSummaryPage(page)
    logging.info(
        "[TEST START] Regression - Scenario: 5: DNA colonoscopy assessment twice"
    )

    # Given I log in to BCSS "England" as user role "Hub Manager"
    user_role = UserTools.user_login(
        page, "Hub Manager at BCS01", return_role_type=True
    )
    if user_role is None:
        raise ValueError("User cannot be assigned to a UserRoleType")

    # And I create a subject that meets the following criteria:
    requirements = {
        "age (y/d)": "64/12",
        "active gp practice in hub/sc": "BCS01/BCS001",
    }
    nhs_no = CreateSubjectSteps().create_custom_subject(requirements)
    if nhs_no is None:
        pytest.fail("Failed to create subject: NHS number not returned.")

    # Then Comment: NHS number
    logging.info(f"[SUBJECT CREATED] NHS number: {nhs_no}")

    # And my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "subject age": "64",
            "subject has episodes": "No",
            "screening status": "Inactive",
        },
    )
    # Assert subject details in the UI
    screening_subject_page_searcher.navigate_to_subject_summary_page(page, nhs_no)
    summary_page.assert_subject_age(64)
    summary_page.assert_screening_status("Inactive")

    # When I run the FOBT failsafe trawl for my subject
    CallAndRecallUtils().run_failsafe(nhs_no)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "subject has episodes": "No",
            "Screening Due Date": "Last Birthday",
            "Screening due date date of change": "Today",
            "Screening Due Date Reason": "Failsafe Trawl",
            "screening status": "Call",
            "Screening Status Date of Change": "Today",
            "Screening Status Reason": "Failsafe Trawl",
        },
    )

    # When I invite my subject for FOBT screening
    CallAndRecallUtils().invite_subject_for_fobt_screening(nhs_no, user_role)

    # Then my subject has been updated as follows:
    subject_assertion(
        nhs_no,
        {
            "latest event status": "S1 Selected for Screening",
            "latest episode kit class": "FIT",
            "latest episode type": "FOBT",
        },
    )

    # Then there is a "S1" letter batch for my subject with the exact title "Pre-invitation (FIT)"
    # When I process the open "S1" letter batch for my subject
    # When I run Timed Events for my subject
    # Then there is a "S9" letter batch for my subject with the exact title "Invitation & Test Kit (FIT)"
    # Then my subject has been updated as follows:
    # batch_processing( TODO: Check these values
    #     page,
    #     "S1",
    #     "Pre-invitation (FIT)",
    #     "S9 - Invitation & Test Kit (FIT)",
    #     True,
    # )


# When I process the open "S9" letter batch for my subject
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	S10 Invitation & Test Kit Sent

# When I log my subject's latest unlogged FIT kit
# And I pause for "6" seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	S43 Kit Returned and Logged (Initial Test)

# When I read my subject's latest logged FIT kit as "ABNORMAL"
# Then my subject has been updated as follows:

# Latest event status	A8 Abnormal

# When I view the subject
# And I choose to book a practitioner clinic for my subject
# And I select "BCS001" as the screening centre where the practitioner appointment will be held
# And I set the practitioner appointment date to "today"
# And I book the "earliest" available practitioner appointment on this date
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	A183 1st Colonoscopy Assessment Appointment Requested
# And there is a "A183" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment"
# And there is a "A183" letter batch for my subject with the exact title "GP Result (Abnormal)"

# When I process the open "A183 - Practitioner Clinic 1st Appointment" letter batch for my subject
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	A25 1st Colonoscopy Assessment Appointment Booked, letter sent

# When I switch users to BCSS "England" as user role "Screening Centre Manager"
# And I view the subject
# And I view the event history for the subject's latest episode
# And I view the latest practitioner appointment in the subject's episode
# And The subject DNAs the practitioner appointment
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	J11 1st Colonoscopy Assessment Appointment Non-attendance (Patient)
# And there is a "J11" letter batch for my subject with the exact title "Practitioner Clinic 1st Appointment Non Attendance (Patient)"

# When I process the open "J11" letter batch for my subject
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	J27 Appointment Non-attendance Letter Sent (Patient)

# When I view the subject
# And I choose to book a practitioner clinic for my subject
# And I select "BCS001" as the screening centre where the practitioner appointment will be held
# And I set the practitioner appointment date to "today"
# And I book the "earliest" available practitioner appointment on this date
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	A184 2nd Colonoscopy Assessment Appointment Requested
# And there is a "A184" letter batch for my subject with the exact title "Practitioner Clinic 2nd Appointment"

# When I process the open "A184 - Practitioner Clinic 2nd Appointment" letter batch for my subject
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	A26 2nd Colonoscopy Assessment Appointment Booked, letter sent

# When I view the subject
# And I view the event history for the subject's latest episode
# And I view the latest practitioner appointment in the subject's episode
# And The subject DNAs the practitioner appointment
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	A185 2nd Colonoscopy Assessment Appointment Non-attendance (Patient)
# And there is a "A185" letter batch for my subject with the exact title "Patient Discharge (Non Attendance of Practitioner Clinic)"

# When I process the open "A185" letter batch for my subject
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	A37 Patient Discharge Sent (Non-attendance at Colonoscopy Assessment Appointment)
# And there is a "A37" letter batch for my subject with the exact title "GP Discharge (Non Attendance of Practitioner Clinic)"

# When I switch users to BCSS "England" as user role "Hub Manager"
# And I process the open "A37" letter batch for my subject
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest event status	P202 Waiting Completion of Outstanding Events

# When I view the subject
# And I view the advance episode options
# And I select the advance episode option for "Record Diagnosis Date"
# And I enter a Diagnosis Date of "today"
# And I save Diagnosis Date Information
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Latest episode diagnosis date reason	Null
# Latest episode has diagnosis date   	Yes
# Latest episode includes event status	A50 Diagnosis date recorded
# Latest event status                 	P202 Waiting Completion of Outstanding Events

# When I process the open "A183 - GP Result (Abnormal)" letter batch for my subject
# And I pause for 5 seconds to let the process complete
# Then my subject has been updated as follows:

# Calculated FOBT due date                 	2 years from latest A37 event
# Calculated lynch due date               	Unchanged
# Calculated surveillance due date         	Unchanged
# Ceased confirmation date                 	Null
# Ceased confirmation details             	Null
# Ceased confirmation user ID             	Null
# Clinical reason for cease               	Null
# Latest episode accumulated result       	Definitive abnormal FOBT outcome
# Latest episode includes event status     	A167 GP Abnormal FOBT Result Sent
# Latest episode recall calculation method	Date of last patient letter
# Latest episode recall episode type       	FOBT Screening
# Latest episode recall surveillance type 	Null
# Latest episode status                   	Closed
# Latest episode status reason             	Non Response
# Latest event status                     	A166 GP Discharge Sent (No show for Colonoscopy Assessment Appointment)
# Lynch due date                           	Null
# Lynch due date date of change           	Unchanged
# Lynch due date reason                   	Unchanged
# Screening due date                       	Calculated FOBT due date
# Screening due date date of change       	Today
# Screening due date reason               	Recall
# Screening status                         	Recall
# Screening status date of change
# Not checking as status may or may not have changed
# Screening status reason                 	Recall
# Surveillance due date                   	Null
# Surveillance due date date of change     	Unchanged
# Surveillance due date reason             	Unchanged
