# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from classes.selection_builder_exception import SelectionBuilderException
from classes.subject_selection_criteria_key import SubjectSelectionCriteriaKey


# Add helper class stubs below
class LatestEpisodeLatestInvestigationDataset:
    NONE = "none"
    COLONOSCOPY_NEW = "colonoscopy_new"
    LIMITED_COLONOSCOPY_NEW = "limited_colonoscopy_new"
    FLEXIBLE_SIGMOIDOSCOPY_NEW = "flexible_sigmoidoscopy_new"
    CT_COLONOGRAPHY_NEW = "ct_colonography_new"
    ENDOSCOPY_INCOMPLETE = "endoscopy_incomplete"
    RADIOLOGY_INCOMPLETE = "radiology_incomplete"

    _mapping = {
        "none": NONE,
        "colonoscopy_new": COLONOSCOPY_NEW,
        "limited_colonoscopy_new": LIMITED_COLONOSCOPY_NEW,
        "flexible_sigmoidoscopy_new": FLEXIBLE_SIGMOIDOSCOPY_NEW,
        "ct_colonography_new": CT_COLONOGRAPHY_NEW,
        "endoscopy_incomplete": ENDOSCOPY_INCOMPLETE,
        "radiology_incomplete": RADIOLOGY_INCOMPLETE,
    }

    @classmethod
    def from_description(cls, description: str) -> str:
        key = description.strip().lower()
        if key not in cls._mapping:
            raise ValueError(f"Unknown investigation dataset filter: '{description}'")
        return cls._mapping[key]


class MockSelectionBuilder:
    """
    Lightweight test harness that mimics SubjectSelectionQueryBuilder behavior.

    This class is used for local testing of SQL fragment builder methods without requiring
    the full application context. Developers can reimplement individual _add_criteria_*
    methods here for isolated evaluation.

    Usage:
        - Add your _add_criteria_* method to this class
        - Then create tests in utils/oracle/test_subject_criteria_dev.py to run it
        - Use dump_sql() to inspect the generated SQL fragment
    """

    def __init__(self, criteria_key, criteria_value, criteria_comparator=">="):
        self.criteria_key = criteria_key
        self.criteria_key_name = criteria_key.description
        self.criteria_value = criteria_value
        self.criteria_comparator = criteria_comparator
        self.criteria_index: int = 0
        self.sql_where = []
        self.sql_from = []

    # Don't delete this method; it is used to inspect the SQL fragments
    def dump_sql(self):
        parts = []

        if self.sql_from:
            parts.append("-- FROM clause --")
            parts.extend(self.sql_from)

        if self.sql_where:
            parts.append("-- WHERE clause --")
            parts.extend(self.sql_where)

        return "\n".join(parts)

    def _add_join_to_latest_episode(self) -> None:
        """
        Mock stub for adding latest episode join. No-op for test harness.
        """
        self.sql_from.append("-- JOIN to latest episode placeholder")

    def _dataset_source_for_criteria_key(self) -> dict:
        """
        Maps criteria key to dataset table and alias.
        """
        key = self.criteria_key
        if key == SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_CANCER_AUDIT_DATASET:
            return {"table": "ds_cancer_audit_t", "alias": "cads"}
        if (
            key
            == SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_COLONOSCOPY_ASSESSMENT_DATASET
        ):
            return {"table": "ds_patient_assessment_t", "alias": "dspa"}
        if key == SubjectSelectionCriteriaKey.LATEST_EPISODE_HAS_MDT_DATASET:
            return {"table": "ds_mdt_t", "alias": "mdt"}
        raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

    # === Example testable method below ===
    # Replace this with the one you want to test,
    # then use utils/oracle/test_subject_criteria_dev.py to run your scenarios

    def _add_criteria_latest_episode_latest_investigation_dataset(self) -> None:
        """
        Filters subjects based on their latest investigation dataset in their latest episode.
        Supports colonoscopy and radiology variations.
        """
        try:
            self._add_join_to_latest_episode()
            value = LatestEpisodeLatestInvestigationDataset.from_description(self.criteria_value)

            if value == "none":
                self.sql_where.append(
                    "AND NOT EXISTS (SELECT 'dsc1' FROM v_ds_colonoscopy dsc1 "
                    "WHERE dsc1.episode_id = ep.subject_epis_id "
                    "AND dsc1.confirmed_type_id = 16002)"
                )
            elif value == "colonoscopy_new":
                self.sql_where.append(
                    "AND EXISTS (SELECT 'dsc2' FROM v_ds_colonoscopy dsc2 "
                    "WHERE dsc2.episode_id = ep.subject_epis_id "
                    "AND dsc2.confirmed_type_id = 16002 "
                    "AND dsc2.deleted_flag = 'N' "
                    "AND dsc2.dataset_new_flag = 'Y')"
                )
            elif value == "limited_colonoscopy_new":
                self.sql_where.append(
                    "AND EXISTS (SELECT 'dsc3' FROM v_ds_colonoscopy dsc3 "
                    "WHERE dsc3.episode_id = ep.subject_epis_id "
                    "AND dsc3.confirmed_type_id = 17996 "
                    "AND dsc3.deleted_flag = 'N' "
                    "AND dsc3.dataset_new_flag = 'Y')"
                )
            elif value == "flexible_sigmoidoscopy_new":
                self.sql_where.append(
                    "AND EXISTS (SELECT 'dsc4' FROM v_ds_colonoscopy dsc4 "
                    "WHERE dsc4.episode_id = ep.subject_epis_id "
                    "AND dsc4.confirmed_type_id = 16004 "
                    "AND dsc4.deleted_flag = 'N' "
                    "AND dsc4.dataset_new_flag = 'Y')"
                )
            elif value == "ct_colonography_new":
                self.sql_where.append(
                    "AND EXISTS (SELECT 'dsr1' FROM v_ds_radiology dsr1 "
                    "WHERE dsr1.episode_id = ep.subject_epis_id "
                    "AND dsr1.confirmed_type_id = 16087 "
                    "AND dsr1.deleted_flag = 'N' "
                    "AND dsr1.dataset_new_flag = 'Y')"
                )
            elif value == "endoscopy_incomplete":
                self.sql_where.append(
                    "AND EXISTS (SELECT 'dsei' FROM v_ds_colonoscopy dsei "
                    "WHERE dsei.episode_id = ep.subject_epis_id "
                    "AND dsei.deleted_flag = 'N' "
                    "AND dsei.dataset_completed_flag = 'N' "
                    "AND dsei.dataset_new_flag = 'N' "
                    "AND dsei.confirmed_test_date >= TO_DATE('01/01/2020','dd/mm/yyyy'))"
                )
            elif value == "radiology_incomplete":
                self.sql_where.append(
                    "AND EXISTS (SELECT 'dsri' FROM v_ds_radiology dsri "
                    "WHERE dsri.episode_id = ep.subject_epis_id "
                    "AND dsri.deleted_flag = 'N' "
                    "AND dsri.dataset_completed_flag = 'N' "
                    "AND dsri.dataset_new_flag = 'N' "
                    "AND dsri.confirmed_test_date >= TO_DATE('01/01/2020','dd/mm/yyyy'))"
                )
            else:
                raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)
