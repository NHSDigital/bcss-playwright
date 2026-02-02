from oracle.oracle import OracleDB
import pandas as pd


def get_nhs_no_from_batch_id(batch_id: str) -> pd.DataFrame:
    """
    This query returns a dataframe of NHS Numbers of the subjects in a certain batch
    We provide the batch ID e.g. 8812 and then we have a list of NHS Numbers we can verify the statuses

    Args:
        batch_id (str): The batch ID you want to get the subjects from

    Returns:
        nhs_number_df (pd.DataFrame): A pandas DataFrame containing the result of the query
    """
    query = """
        SELECT SUBJECT_NHS_NUMBER
        FROM SCREENING_SUBJECT_T ss
        INNER JOIN sd_contact_t c ON ss.subject_nhs_number = c.nhs_number
        INNER JOIN LETT_BATCH_RECORDS lbr
        ON ss.SCREENING_SUBJECT_ID = lbr.SCREENING_SUBJECT_ID
        WHERE lbr.BATCH_ID IN :batch_id
        AND ss.screening_status_id != 4008
        ORDER BY ss.subject_nhs_number
    """
    params = {"batch_id": batch_id}
    nhs_number_df = OracleDB().execute_query(query, params)
    return nhs_number_df


def there_is_letter_batch(
    letter_batch_code: str,
    letter_batch_title: str,
) -> bool:
    """
    This function checks if there is a letter batch with the specified code and title in the database.
    Args:
        letter_batch_code (str): The code of the letter batch to check.
        letter_batch_title (str): The title of the letter batch to check.
    Returns:
        bool: True if the letter batch exists, False otherwise.
    """
    sql_query = """ SELECT lb.batch_id
        FROM lett_batch_records lbr
        INNER JOIN lett_batch lb
        ON lb.batch_id = lbr.batch_id
        INNER JOIN valid_values ld
        ON ld.valid_value_id = lb.description_id
        INNER JOIN valid_values lbs
        ON lbs.valid_value_id = lb.status_id
        WHERE lb.batch_state_id = 12018
        AND lbs.allowed_value = :batch_code
        AND LOWER(ld.description) = LOWER(:batch_title)
        AND lbr.non_inclusion_id IS NULL
        AND lbr.key_id != 11539
        """


    params = {
        "batch_code": letter_batch_code,
        "batch_title": letter_batch_title,
    }

    batch_df = OracleDB().execute_query(sql_query, params)
    if not batch_df.empty:
        return True
    else:
        return False
