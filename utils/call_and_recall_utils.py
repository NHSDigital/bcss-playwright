import logging
import oracledb
from utils.oracle.oracle import OracleDB


class CallAndRecallUtils:
    """
    This contains utility methods to do with Call and Recall
    """

    def __init__(self):
        self.oracledb = OracleDB()

    def run_failsafe(self, nhs_no: str) -> None:
        """
        Run the failsafe trawl for the given NHS number.
        Args:
            nhs_no: The NHS number of the subject
        """
        subject_id = int(self.oracledb.get_subject_id_from_nhs_number(nhs_no))
        conn = self.oracledb.connect_to_db()
        conn.callTimeout = 30000  # Setting call timeout to 30 seconds
        cur = conn.cursor()

        pi = cur.var(oracledb.NUMBER)
        pi.setvalue(0, subject_id)

        out_cursor = cur.var(oracledb.CURSOR)

        cur.execute(
            """
            BEGIN
                pkg_fobt_call.p_failsafe_trawl(
                    pi_subject_id => :pi,
                    po_cur_error  => :po
                );
            END;""",
            {"pi": str(subject_id), "po": out_cursor},
        )

        result_cursor = out_cursor.getvalue()
        row = result_cursor.fetchone()
        assert (
            "The action was performed successfully" in row
        ), f"Error when executing failsafe for {nhs_no}: {row}"

        # Clean up
        result_cursor.close()
        cur.close()
        conn.close()
        logging.info(f"END: failsafe stored proc executed for {nhs_no}")
