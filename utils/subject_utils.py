from datetime import datetime, timedelta
from dataclasses import dataclass
from datetime import datetime


@dataclass
class InvitationPlan:
    """
    Represents a structured view of an active invitation plan returned by
    `get_active_invitation_plan()` in the subject_utils module.

    This dataclass is used primarily in the `test_add_subjects_and_create_invitation_plan`
    test case to verify, augment, and operate on the subject pool for a
    given screening centre and hub. It provides strongly-typed access to
    core scheduling parameters required for dynamic test setup.

    Attributes:
        start_date (datetime): The start date of the invitation plan.
        end_date (datetime): The end date of the invitation plan.
        invitations_per_day (int): How many subjects are currently scheduled per day.
        invitations_due (int): The total number of subjects planned across the duration.
    """

    start_date: datetime
    end_date: datetime
    invitations_per_day: int
    invitations_due: int


def get_active_invitation_plan(hub_code, sc_code, db_connection) -> InvitationPlan:
    """
    Retrieves the currently active invitation plan for a given hub and screening centre.
    Replace with real DB logic using your ORM or SQL execution layer.

    Returns:
        InvitationPlan: Structured representation of the current active plan.
    """
    return InvitationPlan(
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=300),
        invitations_per_day=20,
        invitations_due=4000,
    )


def calculate_subject_shortfall(active_plan: InvitationPlan, daily_target: int) -> int:
    """
    Based on the active plan and the desired daily rate,
    calculate how many new subjects should be added.
    """
    invitations_per_day = active_plan.invitations_per_day
    invitations_due = active_plan.invitations_due
    plan_duration_days = (active_plan.end_date - active_plan.start_date).days

    estimated_total = int(
        (daily_target / invitations_per_day) * invitations_due * 1.01 - invitations_due
    )
    return max(0, estimated_total)


def create_subject(birth_date, screening_centre, hub, region):
    """
    Creates a new subject in the database.
    You’ll likely want to use your existing data generation utilities or raw SQL here.
    """
    # TODO: Implement subject creation logic
    print(
        f"[create_subject] Created subject born {birth_date} for {screening_centre} in {region}"
    )
