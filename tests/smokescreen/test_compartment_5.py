import logging
from math import exp
import pytest
from playwright.sync_api import Page, expect
from pages.logout.log_out_page import Logout
from pages.base_page import BasePage
from pages.screening_practitioner_appointments.screening_practitioner_appointments import (
    ScreeningPractitionerAppointmentsPage,
)
from pages.screening_practitioner_appointments.set_availability_page import (
    SetAvailabilityPage,
)
from pages.screening_practitioner_appointments.practitioner_availability_page import (
    PractitionerAvailabilityPage,
)
from pages.screening_practitioner_appointments.colonoscopy_assessment_appointments_page import (
    ColonoscopyAssessmentAppointments,
)
from pages.screening_practitioner_appointments.book_appointment_page import (
    BookAppointmentPage,
)
from pages.screening_subject_search.subject_screening_summary import (
    SubjectScreeningSummary,
)
from pages.screening_subject_search.episode_events_and_notes_page import (
    EpisodeEventsAndNotesPage,
)
from utils.user_tools import UserTools
from utils.load_properties_file import PropertiesFile
from utils.calendar_picker import CalendarPicker
from utils.batch_processing import batch_processing
from datetime import datetime
from sqlalchemy.orm import Session


@pytest.fixture
def smokescreen_properties() -> dict:
    return PropertiesFile().get_smokescreen_properties()


# --------------
# DATA SETUP
# --------------

# The data setup steps below have been translated directly from the selenium tests and need to be refactored


# Get required test data from the DB
def find_test_data(session: Session, region):
    all_data_found = True
    error_message = ""

    required_number_of_kits = get_properties().get_c5_number_of_appointments_to_attend(
        region
    )
    if required_number_of_kits == 0:
        print("application properties specifies Zero appointments")
    else:
        print("Finding recent appointments")
        appointments = (
            session.query(Appointment)
            .filter(
                Appointment.org_id
                == get_properties().get_appointments_test_org_id(region),
                Appointment.kit_type == KitType.Any,
            )
            .order_by(Appointment.date_created.desc())
            .limit(required_number_of_kits)
            .all()
        )

        if not appointments or len(appointments) < required_number_of_kits:
            all_data_found = False
            error_message = f"{required_number_of_kits} appointments could not be found that had an abnormal result ({region}). Instead found {len(appointments)}"
            print(
                f"{required_number_of_kits} appointments could not be found that had an abnormal result ({region})"
            )
        else:
            print(f"{len(appointments)} appointments found with abnormal results")

    print(
        f"Appointments found: {', '.join([str(appointment.screening_subject.name_and_nhs_number) for appointment in appointments])}"
    )

    return all_data_found, error_message, appointments


# Find subjects requiring screening outcomes
def test_find_subjects_requiring_screening_outcomes(setup_browser, region, page: Page):
    browser, _ = setup_browser
    # Assume testData is initialized somewhere in your test setup.

    # Use SQLAlchemy session to fetch data
    session = get_session(region)  # Replace with actual session setup
    all_data_found, error_message, appointments = find_test_data(session, region)

    assert all_data_found, error_message

    logging.trace("exit: findSubjectsRequiringScreeningOutcomes(region={})", region)

    # --------------
    # TEST STEPS
    # --------------
    @pytest.mark.vpn_required
    @pytest.mark.smokescreen
    @pytest.mark.compartment5
    def test_compartment_5(page: Page, smokescreen_properties: dict) -> None:
        """This is the main compartment 5 method"""

    # --------------
    # Attendance of Screening
    # Practitioner Clinic Appointment
    # --------------

    # Log in as a Screening Centre user
    UserTools.user_login(page, "Screening Centre Manager at BCS001")
    BasePage(page).go_to_screening_practitioner_appointments_page()

    # From the Main Menu, choose the 'Screening Practitioner Appointments' and then 'View Appointments' option
    ScreeningPractitionerAppointmentsPage(page).go_to_view_appointments_page()

    # Select the Appointment Type, Site, and Screening Practitioner
    ScreeningPractitionerAppointmentsPage(page).select_appointment_type(
        "Any Practitioner Appointment"
    )
    ScreeningPractitionerAppointmentsPage(page).select_site_dropdown_option(
        "BCS001 - Wolverhampton Bowel Cancer Screening Centre"
    )
    ScreeningPractitionerAppointmentsPage(page).select_practitioner_dropdown_option(
        "Astonish, Ethanol"
    )
    # Select the required date of the appointment
    # TODO: Add logic to select the date of the appointmentonce the C4 calendar picker is implemented

    # Click 'View appointments on this day' button
    ScreeningPractitionerAppointmentsPage(
        page
    ).click_view_appointments_on_this_day_button()
    # 'View Appointments' screen displayed
    BasePage.bowel_cancer_screening_page_title_contains_text(
        "Screening Practitioner Day View"
    )

    # Select the first positive (abnormal ) patient
    page.get_by_role("link", name="SCALDING COD").click()


# Select Attendance radio button, tick Attended checkbox,
# set Attended Date to yesterday's (system) date and then press Save
# Appointment attendance details saved Status set to J10

# Repeat for the 2nd and 3rd Abnormal patients
# Appointment attendance details saved Status set to J10

# --------------
# Invite for colonoscopy
# --------------
# Navigate to the 'Subject Screening Summary' screen for the 1st Abnormal patient
# ''Subject Screening Summary' screen of the 1st Abnormal patient is displayed

# Click on 'Datasets' link
# 'There should be a '1 dataset' for Colonoscopy Assessment

# Click on 'Show Dataset' next to the Colonoscopy Assessment
# Populate Colonoscopy Assessment Details fields
# ASA Grade  - I - Fit
# Fit for Colonoscopy (SSP) - Yes
# Click 'Yes' for Dataset Complete?
# Click Save Dataset button
# Click Back
# Data set marked as **Completed**. The subject event status stays at J10.

# On the Subject Screening Summary click on the 'Advance FOBT Screening Episode' button and then click on the 'Suitable for Endoscopic Test' button
# Click OK after message
# Pop up message states
# This will change the status to:
# A99 - Suitable for Endoscopic Test.
# No other pop up message should be displayed

# Enter a 'First Offered Appointment Date' (enter a date after the attended appt)

# Select 'Colonoscopy' from the 'Type of Test' from the drop down list

# Click the 'Invite for Diagnostic Test >>' button
# Pop-up box displayed informing user that the patient will be set to A59 - Invited for Diagnostic Test

# Click 'OK'
# Pop-box removed from screen
# 'Advance Screening Episode' redisplayed
# Status set to A59 - Invited for Diagnostic Test

# Click 'Attend Diagnostic Test' button

# Select Colonoscopy from drop down list. Enter the actual appointment date as today's date and select 'Save'
# Status set to A259 - Attended Diagnostic Test

# Repeat for the 2nd & 3rd Abnormal patients
# Status set to A259 - Attended Diagnostic Test

# --------------
# Advance the screening episode
# --------------

# Click on 'Advance FOBT Screening Episode' button for the 1st Abnormal patient

# Click 'Other Post-investigation Contact Required' button
# Confirmation pop-up box displayed

# Click 'OK'
# Status set to A361 - Other Post-investigation Contact Required'Advance FOBT Screening Episode' screen re-displayed

# Select 'Record other post-investigation contact' button
# 'Contact with Patient' screen displayed

# Complete 'Contact Direction',
# 'Contact made between patient and',
# 'Date of Patient Contact',
# 'Start Time', 'End Time',
# 'Discussion Record' and
# select 'Outcome' - 'Post-investigation Appointment Not Required'
# and click 'Save'
# ''Contact with Patient' screen re-displayed readonly

# Click 'Back' button
# ''Subject Screening Summary' screen displayed
# Status set to A323 - Post-investigation Appointment NOT Required

# Repeat for the 2nd & 3rd Abnormal patients
# ''Subject Screening Summary' screen displayed
# Status set to A323 - Post-investigation Appointment NOT Required
