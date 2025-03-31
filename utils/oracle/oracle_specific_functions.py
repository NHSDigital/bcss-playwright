from oracle.oracle import OracleDB
import logging
import pandas as pd

def get_kit_id_from_db() -> pd.DataFrame:
    logging.info("Retrieving useable test kit ids")
    kit_id_df = OracleDB().execute_query("""select tk.kitid, tk.screening_subject_id, sst.subject_nhs_number
    from tk_items_t tk
    inner join ep_subject_episode_t se on se.screening_subject_id = tk.screening_subject_id
    inner join screening_subject_t sst on (sst.screening_subject_id = tk.screening_subject_id)
    inner join sd_contact_t sdc on (sdc.nhs_number = sst.subject_nhs_number)
    where tk.tk_type_id = 2
    and tk.logged_in_flag = 'N'
    and sdc.hub_id = 23159
    and device_id is null
    and tk.invalidated_date is null
    and se.latest_event_status_id in (11198, 11213)
    fetch first 10 rows only""")
    return kit_id_df

def get_nhs_no_from_batch_id(batch_id) -> pd.DataFrame:
    nhs_number_df = OracleDB().execute_query(f"""
    SELECT SUBJECT_NHS_NUMBER
    FROM SCREENING_SUBJECT_T ss
    INNER JOIN sd_contact_t c ON ss.subject_nhs_number = c.nhs_number
    INNER JOIN LETT_BATCH_RECORDS lbr
    ON ss.SCREENING_SUBJECT_ID = lbr.SCREENING_SUBJECT_ID
    WHERE lbr.BATCH_ID IN {batch_id}
    AND ss.screening_status_id != 4008
    ORDER BY ss.subject_nhs_number
    """)
    return nhs_number_df
