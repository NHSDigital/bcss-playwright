# mock_selection_builder.py — Development-only testing harness for criteria logic
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
print("PYTHONPATH set to:", sys.path[0])
from classes.subject_selection_criteria_key import (
    SubjectSelectionCriteriaKey,
)
from classes.episode_type import EpisodeType
from classes.subject_has_episode import SubjectHasEpisode
from classes.selection_builder_exception import SelectionBuilderException


class MockSelectionBuilder:
    """
    Lightweight test harness that mimics SubjectSelectionQueryBuilder behavior.

    This class is meant for local testing of SQL fragment builders without the full
    application context. Developers can copy/paste individual _add_criteria_* methods
    from the real builder and test inputs/outputs directly.

    Usage:
        - Create an instance with a criteria key and value
        - Call the appropriate criteria builder method
        - Use dump_sql() to inspect the resulting SQL
    """

    def __init__(self, criteria_key, criteria_value):
        self.criteria_key = criteria_key
        self.criteria_key_name = criteria_key.description
        self.criteria_value = criteria_value
        self.sql_where = []

    def _add_criteria_subject_has_episodes(self, episode_type=None):
        try:
            value = SubjectHasEpisode.by_description(self.criteria_value.lower())
            if value == SubjectHasEpisode.YES:
                self.sql_where.append(" AND EXISTS ( SELECT 'ep' ")
            elif value == SubjectHasEpisode.NO:
                self.sql_where.append(" AND NOT EXISTS ( SELECT 'ep' ")
            else:
                raise SelectionBuilderException(
                    self.criteria_key_name, self.criteria_value
                )
        except Exception:
            raise SelectionBuilderException(self.criteria_key_name, self.criteria_value)

        self.sql_where.append("   FROM ep_subject_episode_t ep ")
        self.sql_where.append(
            "   WHERE ep.screening_subject_id = ss.screening_subject_id "
        )

        if episode_type is not None:
            self.sql_where.append(
                f"   AND ep.episode_type_id = {episode_type.valid_value_id} "
            )

        if self.criteria_key == SubjectSelectionCriteriaKey.SUBJECT_HAS_AN_OPEN_EPISODE:
            self.sql_where.append("   AND ep.episode_end_date IS NULL ")

        self.sql_where.append(" )")

    def dump_sql(self):
        return "\n".join(self.sql_where)
