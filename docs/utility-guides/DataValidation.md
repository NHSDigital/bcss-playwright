# Utility Guide: Data Validation

The Data Validation Utility can be used to check if there are any duplicate values returned from an SQL query.

## Table of Contents

- [Utility Guide: Data Validation](#utility-guide-data-validation)
  - [Table of Contents](#table-of-contents)
  - [How This Works](#how-this-works)
  - [Using the Data Validation Utility](#using-the-data-validation-utility)
  - [Example usage](#example-usage)

## How This Works

This utility first runs the sql query and then uses functionality from pandas to check if there are duplicate records.<br>
If duplicate records are detected, then it will remove them and re-run the query to replace the dropped records.

## Using the Data Validation Utility

To use this utility import the `DataValidation` class and then call the method `check_for_duplicate_records()`.<br>
Here you will need to provide the SQL query as a multiple line string ensuring that the final line has: **fetch first :subjects_to_retrieve rows only**.<br>
This is necessary as this line is later replaced with an offset if duplicates are found.<br>
You will also need to prove any parameters used in the query as a dictionary

## Example usage

    from utils.data_validation import DataValidation

    def get_kit_id_from_db(
        tk_type_id: int, hub_id: int, no_of_kits_to_retrieve: int
    ) -> pd.DataFrame:

        query = """select tk.kitid, tk.screening_subject_id, sst.subject_nhs_number
        from tk_items_t tk
        inner join ep_subject_episode_t se on se.screening_subject_id = tk.screening_subject_id
        inner join screening_subject_t sst on (sst.screening_subject_id = tk.screening_subject_id)
        inner join sd_contact_t sdc on (sdc.nhs_number = sst.subject_nhs_number)
        where tk.tk_type_id = :tk_type_id
        and tk.logged_in_flag = 'N'
        and sdc.hub_id = :hub_id
        and device_id is null
        and tk.invalidated_date is null
        and se.latest_event_status_id in (:s10_event_status, :s19_event_status)
        order by tk.kitid DESC
        fetch first :subjects_to_retrieve rows only"""

        params = {
            "s10_event_status": SqlQueryValues.S10_EVENT_STATUS,
            "s19_event_status": SqlQueryValues.S19_EVENT_STATUS,
            "tk_type_id": tk_type_id,
            "hub_id": hub_id,
            "subjects_to_retrieve": no_of_kits_to_retrieve,
        }

        kit_id_df = DataValidation().check_for_duplicate_records(query, params)

        return kit_id_df
