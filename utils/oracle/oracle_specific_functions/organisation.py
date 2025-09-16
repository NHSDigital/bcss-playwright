from oracle.oracle import OracleDB
import logging


def delete_organisation_relationships_created_for_test(org_codes: list[str]) -> None:
    """
    Deletes organisation relationships for the given org codes.
    Must be run first due to foreign key constraints.
    Args:
        org_codes (list[str]): A list of organisation codes to delete relationships for.
    """
    placeholders = ", ".join([f":org{i}" for i in range(len(org_codes))])
    subquery = f"SELECT ORG_ID FROM ORG WHERE ORG_CODE IN ({placeholders})"

    query = f"""
    DELETE FROM ORG_RELATIONSHIPS
    WHERE CHILD_ORG_ID IN ({subquery})
    OR PARENT_ORG_ID IN ({subquery})
    """

    params = {f"org{i}": code for i, code in enumerate(org_codes)}
    OracleDB().update_or_insert_data_to_table(query, params)


def delete_people_in_org_created_for_test(org_codes: list[str]) -> None:
    """
    Deletes people in organisations for the given org codes.
    Must be run before deleting organisations due to foreign key constraints.
    Args:
        org_codes (list[str]): A list of organisation codes to delete people in organisations for.
    """
    placeholders = ", ".join([f":org{i}" for i in range(len(org_codes))])
    subquery = f"SELECT ORG_ID FROM ORG WHERE ORG_CODE IN ({placeholders})"

    query = f"""
    DELETE FROM PERSON_IN_ORG
    WHERE ORG_ID IN ({subquery})
    """

    params = {f"org{i}": code for i, code in enumerate(org_codes)}
    OracleDB().update_or_insert_data_to_table(query, params)


def delete_orgs_created_for_test(org_codes: list[str]) -> None:
    """
    Deletes organisations for the given org codes.
    Must be run last due to foreign key constraints.
    Args:
        org_codes (list[str]): A list of organisation codes to delete.
    """
    placeholders = ", ".join([f":org{i}" for i in range(len(org_codes))])
    query = f"""
    DELETE FROM ORG
    WHERE ORG_CODE IN ({placeholders})
    """

    params = {f"org{i}": code for i, code in enumerate(org_codes)}
    OracleDB().update_or_insert_data_to_table(query, params)


def delete_organisations_created_for_test(org_codes: list[str]) -> None:
    """
    Deletes test organisations and related data in correct dependency order.
    Args:
        org_codes (list[str]): A list of organisation codes to delete.
    """
    logging.info("Start: delete_organisations_created_for_test(%s)", org_codes)

    delete_organisation_relationships_created_for_test(org_codes)
    delete_people_in_org_created_for_test(org_codes)
    delete_orgs_created_for_test(org_codes)

    logging.info("End: delete_organisations_created_for_test(%s)", org_codes)


def delete_sites_created_for_test(site_codes: list[str]) -> None:
    """
    Deletes sites from the SITES table based on the given site codes.
    Args:
        site_codes (list[str]): A list of site codes to delete.
    """
    logging.info("Start: delete_sites_created_for_test(%s)", site_codes)

    # Dynamically create placeholders like :site0, :site1, ...
    placeholders = ", ".join([f":site{i}" for i in range(len(site_codes))])
    query = f"""
    DELETE FROM SITES
    WHERE SITE_CODE IN ({placeholders})
    """

    # Bind each site code to its placeholder
    params = {f"site{i}": code for i, code in enumerate(site_codes)}

    OracleDB().update_or_insert_data_to_table(query, params)

    logging.info("End: delete_sites_created_for_test(%s)", site_codes)
