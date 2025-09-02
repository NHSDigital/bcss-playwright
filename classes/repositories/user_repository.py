import logging
from typing import List, Optional, Any
from utils.oracle.oracle import OracleDB
from classes.user_role_type import UserRoleType


class UserRepository:
    """
    Repository class handling database access for users.
    """

    def __init__(self):
        self.oracle_db = OracleDB()

    def get_pio_id_for_role(self, role: "UserRoleType") -> Optional[int]:
        """
        Get the PIO ID for the role.
        """
        logging.info(f"Getting PIO ID for role: {role.user_code}")
        sql = """
            SELECT
                pio.pio_id
            FROM person_in_org pio
            INNER JOIN person prs ON prs.prs_id = pio.prs_id
            INNER JOIN org ON org.org_id = pio.org_id
            WHERE prs.oe_user_code = :user_code
              AND org.org_code = :org_code
              AND pio.role_id = :role_id
              AND pio.is_bcss_user = 1
              AND TRUNC(SYSDATE) BETWEEN TRUNC(pio.start_date) AND NVL(pio.end_date, SYSDATE)
        """
        params = {
            "user_code": role.user_code,
            "org_code": role.org_code,
            "role_id": role.role_id,
        }
        df = self.oracle_db.execute_query(sql, params)
        if not df.empty:
            pio_id = int(df["pio_id"].iloc[0])
            return pio_id
        return None
