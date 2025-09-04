from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass
class Analyser:
    """
    Data class representing an analyser.
    """

    analyser_id: Optional[int] = None
    analyser_code: Optional[str] = None
    hub_id: Optional[int] = None
    analyser_type_id: Optional[int] = None
    spoil_result_code: Optional[int] = None
    tech_fail_result_code: Optional[int] = None
    below_range_result_code: Optional[int] = None
    above_range_result_code: Optional[int] = None

    def __str__(self) -> str:
        return (
            f"Analyser [analyser_id={self.analyser_id}, analyser_code={self.analyser_code}, "
            f"hub_id={self.hub_id}, spoil_result_code={self.spoil_result_code}, "
            f"tech_fail_result_code={self.tech_fail_result_code}, "
            f"below_range_result_code={self.below_range_result_code}, "
            f"above_range_result_code={self.above_range_result_code}]"
        )

    @staticmethod
    def from_dataframe_row(row: pd.Series) -> "Analyser":
        """
        Creates an Analyser object from a pandas DataFrame row containing analyser query results.

        Args:
            row (pd.Series): A row from a pandas DataFrame with columns:
                - tk_analyser_id
                - analyser_code
                - hub_id
                - tk_analyser_type_id

        Returns:
            Analyser: The constructed Analyser object.
        """
        return Analyser(
            analyser_id=row.get("tk_analyser_id"),
            analyser_code=row.get("analyser_code"),
            hub_id=row.get("hub_id"),
            analyser_type_id=row.get("tk_analyser_type_id"),
        )
