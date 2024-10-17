import logging
from contextlib import contextmanager

import psycopg2

from .call import check_call

logger = logging.getLogger(__name__)


def copydb(src, dst):
    check_call(["dropdb", "--if-exists", dst])
    check_call(["createdb", "--template", src, dst])


def psql_file(db, sql_file):
    check_call(["psql", db, "-f", sql_file])


@contextmanager
def cursor(db):
    with psycopg2.connect("dbname=" + db) as conn:
        with conn.cursor() as cr:
            yield cr


def table_exists(cr, table):
    """Check whether a certain table or view exists."""
    cr.execute("SELECT 1 FROM pg_class WHERE relname = %s", (table,))
    return cr.fetchone()


def ref_id(cr, xml_id):
    cr.execute(
        """
    SELECT res_id
    FROM ir_model_data
    WHERE module = %s
        AND name = %s
    """,
        xml_id.split("."),
    )
    result = cr.fetchone()
    return result and result[0] or None


def recover_columns(db_10, db_16, table, columns_to_recover=None):
    """Recover the columns of the specified table.

    This function is useful when you have a table in the source database
    that has columns that are not present in the target database. This
    function will create a copy of the table in the source database and
    then copy the data from the copy table to the target database.

    :param db_10: The name of the source database.
    :param db_16: The name of the target database.
    :param table: The name of the table to recover.
    :param columns_to_recover: A dictionary with the columns to recover
        and their data type. If not specified, the columns will be
        recovered from the source database.
    """
    columns_to_recover = columns_to_recover or {}
    # first we create a complete copy of the product_packaging table
    # into the source database
    logger.info(f"Recovering columns of table {table} from {db_10} to {db_16}.")
    with cursor(db_10) as cr:
        logger.info(f"Creating copy of table {table} in {db_10}.")
        query = f"""
            DROP TABLE IF EXISTS {table}_copy;
            CREATE TABLE {table}_copy AS TABLE {table};
        """
        cr.execute(query)
    # then we copy the data from the copy table to the target database using pg_dump
    # and psql
    with cursor(db_16) as cr:
        logger.info(f"Creating copy of table {table} in {db_16}.")
        query = f"""
            DROP TABLE IF EXISTS {table}_copy;
        """
        cr.execute(query)
    logger.info(f"Copying table {table}_copy from {db_10} to {db_16}.")
    check_call(
        [f"pg_dump -t {table}_copy -d {db_10} | psql -d{db_16}"],
        shell=True,
    )
    # into the target database we ensure that the table has the same structure as the
    # source database and if not we alter it with the missing columns
    with cursor(db_16) as cr:
        query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}'
                """  # E501
        cr.execute(query)
        columns = cr.fetchall()
        columns = {column[0]: column[1] for column in columns}
        query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = '{table}_copy'
                """  # E501
        cr.execute(query)
        columns_copy = cr.fetchall()
        columns_copy = {
            column[0]: column[1]
            for column in columns_copy
            if not columns_to_recover or column[0] in columns_to_recover
        }
        missing_columns = set(columns_copy) - set(columns)
        if missing_columns:
            logger.info("Missing columns in %s table: %s", table, missing_columns)
            for column in missing_columns:
                logger.info(
                    "Adding column %s (%s) to table %s",
                    column,
                    columns_copy[column],
                    table,
                )
                datatype = columns_copy[column]
                if column in columns_to_recover:
                    datatype = columns_to_recover[column]
                query = f"""
                    ALTER TABLE {table}
                    ADD COLUMN {column} {datatype}
                    """
                cr.execute(query)
            # we now copy the data from the copy table to the target table
            logger.info(
                "Copying data from %s_copy to %s for columns %s",
                table,
                table,
                missing_columns,
            )
            query = f"""
                UPDATE {table} SET {", ".join(f"{column} = {table}_copy.{column}" for column in missing_columns)}
                FROM {table}_copy
                WHERE {table}.id = {table}_copy.id
                """
            cr.execute(query)
        # finally we drop the copy table
        query = f"""
            DROP TABLE {table}_copy
            """
        cr.execute(query)


def copytable(db_10, db_16, table):
    """Copy table from db_10 to db_16."""
    logger.info(f"Copying table {table} from {db_10} to {db_16}.")
    check_call(
        [f"pg_dump -t {table} -d {db_10} | psql -d{db_16}"],
        shell=True,
    )
