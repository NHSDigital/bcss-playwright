import pandas as pd
from oracle.oracle import OracleDB
import logging
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from utils.user_tools import UserTools
from classes.subject.subject import Subject


class SubjectSelector:
    """
    Provides helper methods for selecting screening subjects based on preconditions
    required by specific scenarios.
    """

    @staticmethod
    def get_subject_for_manual_cease(criteria: dict) -> str:
        """
        Retrieves a subject NHS number suitable for manual cease,
        based on dynamically provided selection criteria.

        Args:
            criteria (dict): Dictionary of filtering conditions to select a subject.
                Example criteria:
                    {
                        "subject age": "75",
                        "screening status": "Inactive",
                        "subject hub code": "BCS02",
                    }

        Returns:
            str: The NHS number of the selected subject.

        Raises:
            ValueError: If no subject is found matching the criteria.
        """
        logging.info(
            f"[SUBJECT SELECTOR] Searching for subject using criteria: {criteria}"
        )

        hub_code = criteria.get("subject hub code", "BCS02")
        user_details = UserTools.retrieve_user(f"Hub Manager at {hub_code}")
        user = UserTools.get_user_object(user_details)
        subject = Subject()

        query_builder = SubjectSelectionQueryBuilder()
        query, bind_vars = query_builder.build_subject_selection_query(
            criteria=criteria,
            user=user,
            subject=subject,
        )

        logging.debug(
            f"[SUBJECT SELECTOR] Executing query:\n{query}\nWith bind variables: {bind_vars}"
        )
        result_df = OracleDB().execute_query(query, bind_vars)

        if result_df.empty:
            raise ValueError("No subject found for manual cease.")

        nhs_number = result_df["subject_nhs_number"].iloc[0]
        logging.info(f"[SUBJECT SELECTOR] Found subject NHS number: {nhs_number}")
        return nhs_number

    @staticmethod
    def get_subject_for_pre_invitation(criteria: dict) -> str:
        """
        Retrieves a subject NHS number suitable for pre-invitation scenarios,
        based on dynamically provided selection criteria.

        Args:
            criteria (dict): Dictionary of filtering conditions to select a subject.
                Example criteria:
                    {
                        "subject age": "75",
                        "screening status": "Pre-invitation",
                        "subject hub code": "BCS02",
                    }

        Returns:
            str: The NHS number of the selected subject.

        Raises:
            ValueError: If no subject is found matching the criteria.
        """
        logging.info(
            f"[SUBJECT SELECTOR] Searching for pre-invitation subject using criteria: {criteria}"
        )

        hub_code = criteria.get("subject hub code", "BCS02")
        user_details = UserTools.retrieve_user(f"Hub Manager at {hub_code}")
        user = UserTools.get_user_object(user_details)
        subject = Subject()

        query_builder = SubjectSelectionQueryBuilder()
        query, bind_vars = query_builder.build_subject_selection_query(
            criteria=criteria,
            user=user,
            subject=subject,
        )

        logging.debug(
            f"[SUBJECT SELECTOR] Executing query:\n{query}\nWith bind variables: {bind_vars}"
        )
        result_df = OracleDB().execute_query(query, bind_vars)

        if result_df.empty:
            raise ValueError("No subject found for pre-invitation scenario.")

        nhs_number = result_df["subject_nhs_number"].iloc[0]
        logging.info(f"[SUBJECT SELECTOR] Found subject NHS number: {nhs_number}")
        return nhs_number

    @staticmethod
    def get_or_create_subject_for_lynch_self_referral(
        screening_centre: str = "BCS01", base_age: int = 75
    ) -> str:
        """
        Retrieves a subject NHS number suitable for Lynch self-referral scenarios.
        If no subject is found, creates one and returns its NHS number.

        Internally uses the following selection criteria:
            {
                "subject age": "75",
                "subject has lynch diagnosis": "Yes",
                "screening status": "Lynch Self-referral",
                "subject hub code": "BCS01"
            }

        Args:
            screening_centre (str): Screening centre code for subject association.
            base_age (int): Minimum age to filter subject candidates.

        Returns:
            str: The NHS number of the selected or created subject.
        """
        from utils.oracle.oracle import OracleSubjectTools  # avoid circular import

        criteria = {
            "subject age": str(base_age),
            "subject has lynch diagnosis": "Yes",
            "screening status": "Lynch Self-referral",
            "subject hub code": screening_centre,
        }

        logging.info(
            "[SUBJECT SELECTOR] Attempting to find or create Lynch self-referral subject"
        )
        user_details = UserTools.retrieve_user(f"Hub Manager at {screening_centre}")
        user = UserTools.get_user_object(user_details)
        subject = Subject()
        query_builder = SubjectSelectionQueryBuilder()

        query, bind_vars = query_builder.build_subject_selection_query(
            criteria=criteria,
            user=user,
            subject=subject,
        )
        result_df = OracleDB().execute_query(query, bind_vars)

        if not result_df.empty:
            nhs_number = result_df["subject_nhs_number"].iloc[0]
            logging.info(
                f"[SUBJECT SELECTOR] Found existing subject NHS number: {nhs_number}"
            )
            return nhs_number

        logging.warning("[SUBJECT SELECTOR] No existing subject found — creating one")
        nhs_number = OracleSubjectTools().create_self_referral_ready_subject(
            screening_centre=screening_centre,
            base_age=base_age,
        )
        logging.info(
            f"[SUBJECT CREATED - LYNCH SELF-REFERRAL] NHS number: {nhs_number}"
        )

        nhs_df = pd.DataFrame({"subject_nhs_number": [nhs_number]})
        OracleDB().exec_bcss_timed_events(nhs_df)

        return nhs_number
