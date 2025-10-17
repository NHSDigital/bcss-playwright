import logging
import random
from datetime import datetime, timedelta
from classes.date.date_description_utils import (
    DateDescriptionUtils,
)
from classes.repositories.general_repository import GeneralRepository
from classes.screening.region_type import RegionType
from classes.subject_selection_query_builder.selection_builder_exception import (
    SelectionBuilderException,
)
from classes.data.data_creation import DataCreation
from classes.repositories.word_repository import WordRepository
from classes.repositories.subject_repository import SubjectRepository
from classes.user.user import User
from classes.user.user_role_type import UserRoleType
from utils import nhs_number_tools
from utils.oracle.oracle import OracleDB
from utils.oracle.subject_selection_query_builder import SubjectSelectionQueryBuilder
from classes.subject.gender_type import GenderType
from classes.lynch.genetic_condition_type import GeneticConditionType

DATE_FORMAT_DD_MM_YYYY = "%d-%m-%Y"
DATE_OF_BIRTH_DESCRIPTION = "DOB"
DIAGNOSIS_DATE_DESCRIPTION = "Diagnosis date description"
LAST_COLONOSCOPY_DATE_DESCRIPTION = "Last colonoscopy date description"
DATE_OF_BIRTH_DESCRIPTION = "Date of birth description"


def insert_validated_lynch_patient_from_new_subject_with_age(
    age: str,
    gene: str,
    when_diagnosis_took_place: str,
    when_last_colonoscopy_took_place: str,
    user_role: UserRoleType,
) -> str:
    logging.debug(
        f"[START] insert_validated_lynch_patient_from_new_subject_with_age({age}, {gene}, {when_diagnosis_took_place}, {when_last_colonoscopy_took_place})"
    )

    PLUS = "+"
    MINUS = "-"
    PLUS_WORD = "plus"
    LESS = "less"
    INVALID_AGE_PARAMETER_FORMAT_MESSAGE = (
        "age (should be format 'NN', 'NN + days' or 'NN - days')"
    )

    try:
        if age.endswith(" days") or age.endswith(" day"):
            age_parts = age.split(" ")
            if len(age_parts) != 4:
                raise SelectionBuilderException(
                    INVALID_AGE_PARAMETER_FORMAT_MESSAGE, age
                )
            years = int(age_parts[0])
            plus_or_minus = age_parts[1]
            if plus_or_minus not in [PLUS, MINUS, PLUS_WORD, LESS]:
                raise SelectionBuilderException(
                    INVALID_AGE_PARAMETER_FORMAT_MESSAGE, age
                )
            days = int(age_parts[2])
        else:
            years = int(age)
            days = random.randint(0, 363)
            plus_or_minus = PLUS
    except Exception:
        raise SelectionBuilderException(INVALID_AGE_PARAMETER_FORMAT_MESSAGE, age)

    date_of_birth = datetime.today().date().replace(day=15, month=10) - timedelta(
        days=years * 365
    )
    if plus_or_minus in [MINUS, LESS]:
        date_of_birth += timedelta(days=days)
    else:
        date_of_birth -= timedelta(days=days)

    date_of_birth_str = str(DateDescriptionUtils.convert_description_to_sql_date(
        DATE_OF_BIRTH_DESCRIPTION, date_of_birth.strftime(DATE_FORMAT_DD_MM_YYYY)
    ))
    if date_of_birth_str is None:
        raise SelectionBuilderException(
            "Failed to convert date of birth to SQL date.", date_of_birth_str
        )

    nhs_number = insert_validated_lynch_patient_from_new_subject(
        date_of_birth_str,
        gene,
        when_diagnosis_took_place,
        when_last_colonoscopy_took_place,
        user_role,
    )

    logging.debug("[END] insert_validated_lynch_patient_from_new_subject_with_age")
    return nhs_number


def insert_validated_lynch_patient_from_new_subject(
    date_of_birth: str,
    gene: str,
    when_diagnosis_took_place: str,
    when_last_colonoscopy_took_place: str,
    user_role: UserRoleType,
) -> str:
    logging.debug(
        f"[START] insert_validated_lynch_patient_from_new_subject({date_of_birth}, {gene}, {when_diagnosis_took_place}, {when_last_colonoscopy_took_place})"
    )

    # Generate random new subject details
    data_creation = DataCreation()
    word_repo = WordRepository()
    subject_repo = SubjectRepository()

    pi_subject = data_creation.generate_random_subject(
        word_repo.get_random_subject_details(),
        "NEW LYNCH TEST SUBJECT",
        region=RegionType.get_region("England"),
    )

    # Ensure NHS number is unique
    attempts = 1
    max_attempts = 100
    if pi_subject.nhs_number is None:
        raise SelectionBuilderException(
            "Generated NHS number is None.", pi_subject.nhs_number
        )
    while (
        subject_repo.find_by_nhs_number(pi_subject.nhs_number) is not None
        and attempts <= max_attempts
    ):
        pi_subject.nhs_number = (
            nhs_number_tools.NHSNumberTools.generate_random_nhs_number()
        )
        attempts += 1

    if attempts > max_attempts:
        logging.error("Failed to find unused random NHS number in 100 tries")
    else:
        delete_validated_lynch_patient(pi_subject.nhs_number)

        sql_query = insert_into_validated_lynch_patients_query_root(
            gene, when_diagnosis_took_place, when_last_colonoscopy_took_place
        )

        # ...existing code...
        def safe_str(value):
            return value if value is not None else ""

        sql_query += add_sql_string_column(
            "nhs_number", safe_str(pi_subject.nhs_number)
        )
        sql_query += add_sql_string_column("title", safe_str(pi_subject.name_prefix))
        sql_query += add_sql_string_column(
            "family_name", safe_str(pi_subject.family_name)
        )
        sql_query += add_sql_string_column(
            "given_name", safe_str(pi_subject.first_given_names)
        )
        sql_query += add_sql_string_column(
            "other_names", safe_str(pi_subject.other_given_names)
        )
        sql_query += add_sql_string_column(
            "address_line_1", safe_str(pi_subject.address_line_1)
        )
        sql_query += add_sql_string_column(
            "address_line_2", safe_str(pi_subject.address_line_2)
        )
        sql_query += add_sql_string_column(
            "address_line_3", safe_str(pi_subject.address_line_3)
        )
        sql_query += add_sql_string_column(
            "address_line_4", safe_str(pi_subject.address_line_4)
        )
        sql_query += add_sql_string_column(
            "address_line_5", safe_str(pi_subject.address_line_5)
        )
        sql_query += add_sql_string_column("postcode", safe_str(pi_subject.postcode))
        sql_query += add_sql_date_column("date_of_birth", date_of_birth)
        gender_code = (
            pi_subject.gender_code if pi_subject.gender_code is not None else 0
        )  # Use 0 or another default
        gender_type = GenderType.by_redefined_value(gender_code)
        gender_value = (
            gender_type.allowed_value if gender_type is not None else "Unknown"
        )

        sql_query += add_sql_string_column(
            "gender",
            gender_value,
        )
        user = User.from_user_role_type(user_role)
        org_code = (
            user.organisation.code
            if user.organisation and user.organisation.code is not None
            else "Unknown"
        )

        sql_query += (
            "(SELECT gp.org_code FROM gp_practice_current_links gpl "
            "INNER JOIN org gp ON gp.org_id = gpl.gp_practice_id "
            "INNER JOIN org hub ON hub.org_id = gpl.hub_id "
            f"WHERE hub.org_code = {SubjectSelectionQueryBuilder.single_quoted(org_code)} "
            "ORDER BY DBMS_RANDOM.random FETCH FIRST 1 ROW ONLY) AS gp_practice_code "
            "FROM dual"
        )

        db_query = OracleDB()
        logging.info(f"Executing query: {sql_query}")
        rows_affected = db_query.update_or_insert_data_to_table(sql_query, {})
        logging.info(f"Rows affected = {rows_affected}")

    process_new_lynch_patients()

    logging.debug("[END] insert_validated_lynch_patient_from_new_subject")
    return pi_subject.nhs_number


def delete_validated_lynch_patient(nhs_number):

    sql_query = []
    sql_query.append(
        f"DELETE FROM validated_lynch_patients WHERE nhs_number = '{nhs_number}'"
    )
    sql_query_str = "".join(sql_query)
    db_query = OracleDB()
    db_query.update_or_insert_data_to_table(sql_query_str, {})


def insert_into_validated_lynch_patients_query_root(
    gene, when_diagnosis_took_place, when_last_colonoscopy_took_place
):
    logging.debug(
        f"[START] insert_into_validated_lynch_patients_query_root({gene}, {when_diagnosis_took_place}, {when_last_colonoscopy_took_place})"
    )

    # Check the gene is valid
    try:
        GeneticConditionType.by_description(gene)
    except Exception:
        raise SelectionBuilderException("Genetic Condition", gene)

    diagnosis_date = DateDescriptionUtils.convert_description_to_sql_date(
        DIAGNOSIS_DATE_DESCRIPTION, when_diagnosis_took_place
    )
    last_colonoscopy_date = DateDescriptionUtils.convert_description_to_sql_date(
        LAST_COLONOSCOPY_DATE_DESCRIPTION, when_last_colonoscopy_took_place
    )

    sql_query = (
        "INSERT INTO validated_lynch_patients ( "
        "gene, diagnosis_date, last_colonoscopy_date, genetics_team, processing_status, "
        "created_datestamp, updated_datestamp, audit_reason, consultant, registry_id, file_name, "
        "nhs_number, title, family_name, given_name, other_names, date_of_birth, gender, "
        "address_line_1, address_line_2, address_line_3, address_line_4, address_line_5, postcode, gp_practice_code) "
        "SELECT "
        f"{SubjectSelectionQueryBuilder.single_quoted(gene)} AS gene, "
        f"{diagnosis_date} AS diagnosis_date, "
        f"{last_colonoscopy_date} AS last_colonoscopy_date, "
        "(SELECT site_code FROM sites WHERE site_type_id = 306448 AND end_date IS NULL ORDER BY DBMS_RANDOM.random FETCH FIRST 1 ROW ONLY) AS genetics_team, "
        "'BCSS_READY' AS processing_status, "
        "SYSDATE AS created_datestamp, "
        "SYSDATE AS updated_datestamp, "
        "'AUTO TESTING' AS audit_reason, "
        "'PROFESSOR AUTO TESTING' AS consultant, "
        "1234 AS registry_id, "
        "'AUTO_TESTING.csv' AS file_name, "
    )

    logging.debug("[END] insert_into_validated_lynch_patients_query_root")
    return sql_query


def add_sql_string_column(column_name: str, column_value: str) -> str:
    logging.debug(f"[START] add_sql_string_column({column_name}, {column_value})")

    if column_value is None:
        query_column = "NULL"
    else:
        safe_value = column_value.replace("'", "''")
        query_column = SubjectSelectionQueryBuilder.single_quoted(safe_value)
    query_column += f" as {column_name}, "

    logging.debug("[END] add_sql_string_column")
    return query_column


def add_sql_date_column(column_name: str, date_string: str) -> str:
    logging.debug(f"[START] add_sql_date_column({column_name}, {date_string})")

    if date_string is None:
        query_column = "NULL"
    else:
        query_column = date_string
    query_column += f" as {column_name}, "

    logging.debug("[END] add_sql_date_column")
    return query_column


def process_new_lynch_patients():
    logging.debug("[START] process_new_lynch_patients")

    general_repository = GeneralRepository()
    general_repository.process_new_lynch_patients()

    logging.debug("[END] process_new_lynch_patients")
