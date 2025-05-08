import pandas as pd
import logging
from oracle.oracle import OracleDB


class DataValidation:
    """
    This class will be used to validate that there are no duplicate records when obtaining test data.
    """

    def __init__(self):
        self.max_attempts = 5

    def check_for_duplicate_records(self, query: str, params: dict) -> pd.DataFrame:
        """
        This method is used to firstly obtain the test data, and then to check if there are any duplicate records.

        Args:
            query (str): The SQL query you want to run
            params (dict): A dictionary of any parameters in the sql query

        Returns:
            dataframe (pd.DataFrame): A dataframe containing 0 duplicate records
        """
        wanted_subject_count = int(params["subjects_to_retrieve"])

        dataframe = OracleDB().execute_query(query, params)

        attempts = 0
        while attempts < self.max_attempts:
            logging.info(f"Checking for duplicates. On attempt: {attempts+1}")
            duplicate_rows_count = int(dataframe.duplicated().sum())

            if duplicate_rows_count == 0:
                logging.info("No duplicate records found")
                return dataframe

            logging.warning(
                f"{duplicate_rows_count} duplicate records found. Dropping duplicates and retrying query."
            )
            dataframe = dataframe.drop_duplicates()
            attempts += 1
            dataframe = self.run_query_for_dropped_records(
                dataframe,
                query,
                params,
                duplicate_rows_count,
                wanted_subject_count,
                attempts,
            )

        logging.error(
            f"Maximum attempt limit of {self.max_attempts} reached. Returning dataframe with duplicates dropped and not replaced."
        )
        dataframe = dataframe.drop_duplicates()
        actual_subject_count = len(dataframe)
        if wanted_subject_count != actual_subject_count:
            logging.error(
                f"Actual subject count differs to wanted count. {wanted_subject_count} subjects wanted but only {actual_subject_count} subjects were retrieved"
            )
        return dataframe

    def run_query_for_dropped_records(
        self,
        dataframe: pd.DataFrame,
        query: str,
        params: dict,
        duplicate_count: int,
        wanted_subject_count: int,
        attempts: int,
    ) -> pd.DataFrame:
        """
        This is used to make up for any dropped duplicate records. It runs the same query again but only returns the amount of dropped records.

        Args:
            dataframe (pd.DataFrame): The dataframe with duplicates dropped
            query (str): The SQL query you want to run
            params (dict): A dictionary of any parameters in the sql query
            duplicate_count (int): The number of duplicate records in the original dataframe
            wanted_subject_count (int): The number of subjects to retrieve in the original query
            attempts (int): The number of attempts so far

        Returns:
            dataframe_without_duplicates (pd.DataFrame): A dataframe matching the original record count
        """
        params["offset_value"] = wanted_subject_count + attempts
        params["subjects_to_retrieve"] = duplicate_count

        query = query.strip().split("\n")
        query[-1] = (
            "OFFSET :offset_value ROWS FETCH FIRST :subjects_to_retrieve rows only"
        )
        query = "\n".join(query)

        dataframe_with_new_subjects = OracleDB().execute_query(query, params)

        combined_dataframe = pd.concat(
            [dataframe, dataframe_with_new_subjects], ignore_index=True
        )
        return combined_dataframe
