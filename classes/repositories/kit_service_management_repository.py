import logging
from typing import Optional
from utils.oracle.oracle import OracleDB
from classes.kit_service_management_record import KitServiceManagementRecord
from classes.entities.kit_service_management_entity import KitServiceManagementEntity


class KitServiceManagementRepository:
    """
    Repository for managing kit service management records.
    """

    def __init__(self):
        self.oracle_db = OracleDB()

    def get_service_management_sql(
        self,
        device_id: Optional[str],
        archived: Optional[bool],
        issuing_hub_id: int,
        logged_hub_id: int,
        status: Optional[str],
        if_error_has_id: Optional[bool],
        order_by_column: str,
    ) -> str:
        """
        Constructs the SQL query for kit service management records.
        """
        sql_query = [
            """
        SELECT kq.device_id, kq.test_kit_name, kq.test_kit_type, kq.test_kit_status,
            CASE WHEN tki.logged_in_flag = 'Y' THEN kq.logged_by_hub END as logged_by_hub,
            CASE WHEN tki.logged_in_flag = 'Y' THEN kq.date_time_logged END as date_time_logged,
            tki.logged_in_on AS tk_logged_date_time,
            kq.test_result, kq.calculated_result, kq.error_code,
            (SELECT vvt.description FROM tk_analyser_t tka INNER JOIN tk_analyser_type_error tkate ON tkate.tk_analyser_type_id = tka.tk_analyser_type_id INNER JOIN valid_values vvt ON tkate.tk_analyser_error_type_id = vvt.valid_value_id WHERE tka.analyser_code = kq.analyser_code AND tkate.error_code = kq.error_code) AS analyser_error_description,
            kq.analyser_code, kq.date_time_authorised, kq.authoriser_user_code, kq.datestamp, kq.bcss_error_id,
            REPLACE (mt.description, 'ERROR - ', '') AS error_type, NVL(mta.allowed_value, 'N') AS error_ok_to_archive,
            kq.post_response, kq.post_attempts, kq.put_response, kq.put_attempts, kq.date_time_error_archived, kq.error_archived_user_code,
            sst.screening_subject_id, sst.subject_nhs_number, tki.test_results, tki.issue_date, o.org_code AS issued_by_hub
        FROM kit_queue kq
        LEFT OUTER JOIN tk_items_t tki ON tki.device_id = kq.device_id OR (tki.device_id IS NULL AND tki.kitid = pkg_test_kit.f_get_kit_id_from_device_id (kq.device_id))
        LEFT OUTER JOIN screening_subject_t sst ON sst.screening_subject_id = tki.screening_subject_id
        LEFT OUTER JOIN ep_subject_episode_t ep ON ep.subject_epis_id = tki.subject_epis_id
        LEFT OUTER JOIN message_types mt ON kq.bcss_error_id = mt.message_type_id
        LEFT OUTER JOIN valid_values mta ON mta.valid_value_id = mt.message_attribute_id AND mta.valid_value_id = 305482
        LEFT OUTER JOIN ORG o ON ep.start_hub_id = o.org_id
        LEFT OUTER JOIN ORG lo ON lo.org_code = kq.logged_by_hub
        WHERE kq.test_kit_type = 'FIT'
        """
        ]

        if device_id:
            sql_query.append("AND kq.device_id = :device_id")
        else:
            # Archived filter
            if archived is not None:
                if archived:
                    sql_query.append("AND kq.date_time_error_archived IS NOT NULL")
                else:
                    sql_query.append("AND kq.date_time_error_archived IS NULL")
            # Hub filters
            if issuing_hub_id > -1 and logged_hub_id > -1:
                sql_query.append(
                    "AND (lo.org_id = :logged_hub_id OR ep.start_hub_id = :issuing_hub_id)"
                )
            elif issuing_hub_id > -1:
                sql_query.append("AND ep.start_hub_id = :issuing_hub_id")
            elif logged_hub_id > -1:
                sql_query.append("AND lo.org_id = :logged_hub_id")
            # Status/error filters
            if status:
                if status.upper() == "ERROR":
                    sql_query.append("AND kq.test_kit_status = 'ERROR'")
                    if if_error_has_id is not None:
                        if if_error_has_id:
                            sql_query.append("AND kq.bcss_error_id IS NOT NULL")
                        else:
                            sql_query.append("AND kq.bcss_error_id IS NULL")
                else:
                    sql_query.append(f"AND kq.test_kit_status = '{status.upper()}'")
            else:
                sql_query.append(
                    "AND (kq.test_kit_status = 'COMPLETE' OR (kq.test_kit_status = 'ERROR'"
                )
                if if_error_has_id is not None:
                    if if_error_has_id:
                        sql_query.append("AND kq.bcss_error_id IS NOT NULL))")
                    else:
                        sql_query.append("AND kq.bcss_error_id IS NULL))")
        if not device_id:
            sql_query.append(f"ORDER BY {order_by_column} DESC NULLS LAST")
        return "\n".join(sql_query)

    def get_service_management(
        self,
        device_id: Optional[str],
        issuing_hub_id: int,
        logged_hub_id: int,
        status: Optional[str],
        archived: Optional[bool],
        if_error_has_id: Optional[bool],
        order_by_column: str,
    ) -> KitServiceManagementRecord:
        """
        Gets kit service management records based on the provided filters.
        """
        logging.info("begin KitServiceManagementRepository.get_service_management")
        sql = self.get_service_management_sql(
            device_id,
            archived,
            issuing_hub_id,
            logged_hub_id,
            status,
            if_error_has_id,
            order_by_column,
        )
        params = {}
        if device_id:
            params["device_id"] = device_id
        else:
            if issuing_hub_id > -1:
                params["issuing_hub_id"] = issuing_hub_id
            if logged_hub_id > -1:
                params["logged_hub_id"] = logged_hub_id
        df = self.oracle_db.execute_query(sql, params)
        return KitServiceManagementRecord().from_dataframe_row(df.iloc[0])

    def get_service_management_by_device_id(
        self, device_id: str
    ) -> KitServiceManagementRecord:
        """
        Gets the kit service management record for the specified device ID.
        """
        logging.info(
            "start: KitServiceManagementRepository.get_service_management_by_device_id"
        )
        kit_queue_record = self.get_service_management(
            device_id=device_id,
            issuing_hub_id=-1,
            logged_hub_id=-1,
            status="",
            archived=None,
            if_error_has_id=None,
            order_by_column="date_time_logged",
        )
        logging.info(
            "exit: KitServiceManagementRepository.get_service_management_by_device_id"
        )
        return kit_queue_record

    def update_kit_service_management_record(
        self, record: KitServiceManagementRecord
    ) -> None:
        """
        Updates a kit service management record in the database.

        Args:
            record (KitServiceManagementRecord): The record to update.
        """
        entity = KitServiceManagementEntity().from_record(record)
        self.update_kit_service_management_entity(entity)

    def update_kit_service_management_entity(
        self, entity: KitServiceManagementEntity
    ) -> None:
        """
        Updates a kit service management entity in the database.
        """

        try:
            sql_query = f"""
            UPDATE kit_queue kq SET
                kq.test_kit_name = :test_kit_name,
                kq.test_kit_type = :test_kit_type,
                kq.test_kit_status = :test_kit_status,
                kq.logged_by_hub = :logged_by_hub,
                kq.date_time_logged = :date_time_logged,
                kq.test_result = {'null' if entity.test_result is None else ':test_result'},
                kq.error_code = {'null' if entity.error_code is None else ':error_code'},
                kq.analyser_code = :analyser_code,
                kq.date_time_authorised = :date_time_authorised,
                kq.authoriser_user_code = :authoriser_user_code,
                kq.post_response = {'null' if entity.post_response is None else ':post_response'},
                kq.post_attempts = {'null' if entity.post_attempts is None else ':post_attempts'},
                kq.put_response = {'null' if entity.put_response is None else ':put_response'},
                kq.put_attempts = {'null' if entity.put_attempts is None else ':put_attempts'},
                kq.datestamp = SYSTIMESTAMP
            WHERE kq.device_id = :device_id
            """

            params = {
                "device_id": entity.device_id,
                "test_kit_name": entity.test_kit_name,
                "test_kit_type": entity.test_kit_type,
                "test_kit_status": entity.test_kit_status,
                "logged_by_hub": entity.logged_by_hub,
                "date_time_logged": entity.date_time_logged,
                "analyser_code": entity.analyser_code,
                "date_time_authorised": entity.date_time_authorised,
                "authoriser_user_code": entity.authoriser_user_code,
            }
            if entity.test_result is not None:
                params["test_result"] = entity.test_result
            if entity.error_code is not None:
                params["error_code"] = entity.error_code
            if entity.post_response is not None:
                params["post_response"] = entity.post_response
            if entity.post_attempts is not None:
                params["post_attempts"] = entity.post_attempts
            if entity.put_response is not None:
                params["put_response"] = entity.put_response
            if entity.put_attempts is not None:
                params["put_attempts"] = entity.put_attempts

            self.oracle_db.update_or_insert_data_to_table(sql_query, params)
        except Exception as ex:
            raise RuntimeError(f"Error updating KIT_QUEUE record: {ex}")
