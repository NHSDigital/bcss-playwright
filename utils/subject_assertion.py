from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.oracle.oracle import OracleDB
from classes.subject import Subject
from classes.user import User
import logging


def subject_assertion(nhs_number: str, criteria: dict) -> bool:
    """
    Asserts that a subject with the given NHS number exists and matches the provided criteria.
    Args:
        nhs_number (str): The NHS number of the subject to find.
        criteria (dict): A dictionary of criteria to match against the subject's attributes.
    Returns:
        bool: True if the subject matches the provided criteria, False if it does not.
    """
    nhs_no_criteria = {"nhs number": nhs_number}
    subject = Subject()
    user = User()
    builder = SubjectSelectionQueryBuilder()

    query, bind_vars = builder.build_subject_selection_query(
        criteria=nhs_no_criteria,
        user=user,
        subject=subject,
        subjects_to_retrieve=1,
    )

    subject_df = OracleDB().execute_query(query, bind_vars)
    subject = Subject.from_dataframe_row(subject_df.iloc[0])

    criteria["nhs number"] = nhs_number
    query, bind_vars = builder.build_subject_selection_query(
        criteria=criteria,
        user=user,
        subject=subject,
        subjects_to_retrieve=1,
    )

    df = OracleDB().execute_query(query, bind_vars)

    if nhs_number in df["subject_nhs_number"].values:
        return True

    # Try removing criteria one by one (except nhs number)
    failed_criteria = []
    criteria_keys = [key for key in criteria if key != "nhs number"]
    for key in criteria_keys:
        reduced_criteria = {key: value for key, value in criteria.items() if key != key}
        query, bind_vars = builder.build_subject_selection_query(
            criteria=reduced_criteria,
            user=user,
            subject=subject,
            subjects_to_retrieve=1,
        )
        df = OracleDB().execute_query(query, bind_vars)
        if nhs_number in df["subject_nhs_number"].values:
            failed_criteria.append((key, criteria[key]))
            break
        else:
            failed_criteria.append((key, criteria[key]))

    if failed_criteria:
        log_message = "Subject Assertion Failed\nFailed criteria:\n" + "\n".join(
            [f"Key: '{key}' - Value: '{value}'" for key, value in failed_criteria]
        )
        logging.error(log_message)
    return False
