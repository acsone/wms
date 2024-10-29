import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import closing, contextmanager

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import odoo

dbname = os.environ["DB_NAME"]

logger = logging.getLogger(__name__)


model_record_to_keep = [
    "account.tax",
    "auth.jwt.validator",
    "delivery.carrier",
    "mail.template",
    "product.pricelist",
    "product.product",
    "product.template",
    "report.paperformat",
    "res.groups",
    "res.partner",
    "res.users",
    "se.backend",
    "se.index.config",
    "shopfloor.menu",
    "shopfloor.profile",
    "stock.location",
    "stock.package.type",
    "stock.picking.type",
    "stock.route",
    "stock.storage.category.capacity",
    "stock.storage.location.sequence",
    "storage.backend",
    "ir.sequence",
]


def _connection_info_for(db_name):
    _db_or_uri, connection_info = odoo.sql_db.connection_info_for(db_name)
    return connection_info


def delete_records_in_chunk(table_name, chunk_ids, connection_info):
    try:
        conn = psycopg2.connect(**connection_info)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with closing(conn.cursor()) as cr:
            delete_query = f"DELETE FROM {table_name} WHERE id IN %s"
            cr.execute(delete_query, (tuple(chunk_ids),))
        conn.close()
        logger.info(f"Deleted records in chunk: {chunk_ids}")
    except Exception as e:
        logger.info(f"Error in chunk {chunk_ids}: {e}")


def parallel_delete(
    table_name, record_ids, connection_info, chunk_size=1000, max_workers=10
):
    chunks = [
        record_ids[i : i + chunk_size] for i in range(0, len(record_ids), chunk_size)
    ]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(delete_records_in_chunk, table_name, chunk, connection_info)
            for chunk in chunks
        ]
        for future in as_completed(futures):
            future.result()  # Raise exception if any


def create_fk_index_ir_attachment(connection_info):
    # create the missing index for FK to ir_attachment
    # to speed up the delete operation
    conn = psycopg2.connect(**connection_info)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with closing(conn.cursor()) as cr:
        query = """
            WITH fk_columns AS (
                SELECT
                    tc.table_schema,
                    tc.table_name AS referencing_table,
                    kcu.column_name AS referencing_column,
                    ccu.table_name AS referenced_table,
                    ccu.column_name AS referenced_column,
                    tc.constraint_name
                FROM
                    information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                WHERE
                    tc.constraint_type = 'FOREIGN KEY'
                    AND ccu.table_name = 'ir_attachment'
            )
            SELECT
                fk.referencing_table,
                fk.referencing_column,
                fk.constraint_name,
                ix.indexname IS NOT NULL AS has_index
            FROM
                fk_columns AS fk
                LEFT JOIN pg_indexes AS ix
                ON fk.referencing_table = ix.tablename
                AND ix.indexdef LIKE '%' || fk.referencing_column || '%';
            """
        cr.execute(query)
        foreign_keys = cr.fetchall()

        for fk in foreign_keys:
            referencing_table, referencing_column, constraint_name, has_index = fk
            if not has_index:
                index_name = f"{referencing_table}_{referencing_column}_manidx"
                create_index_query = f"CREATE INDEX {index_name} ON {referencing_table} ({referencing_column});"
                logger.info(
                    f"Creating index {index_name} on {referencing_table}({referencing_column})..."
                )
                cr.execute(create_index_query)


def delete_round_instance_mail_message(connection_info):
    conn = psycopg2.connect(**connection_info)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with closing(conn.cursor()) as cr:
        cr.execute(
            """
            SELECT id from mail_message
            WHERE model = 'round.instance'
            """
        )
        mail_message_ids = [i[0] for i in cr.fetchall()]
    logger.info("Deleting %d records from mail_message", len(mail_message_ids))
    parallel_delete(
        "mail_message",
        mail_message_ids,
        connection_info,
        chunk_size=1000,
        max_workers=10,
    )


def delete_round_instance_ir_attachment(connection_info):
    conn = psycopg2.connect(**connection_info)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with closing(conn.cursor()) as cr:
        cr.execute(
            """
            SELECT id, store_fname from ir_attachment
            WHERE res_model = 'round.instance'
            """
        )
        ir_attachment_ids = [i[0] for i in cr.fetchall()]
        fnames = [i[1] for i in cr.fetchall()]
    logger.info("Deleting %d records from ir_attachment", len(ir_attachment_ids))
    parallel_delete(
        "ir_attachment",
        ir_attachment_ids,
        connection_info,
        chunk_size=1000,
        max_workers=10,
    )
    logger.info("Deleting %d files from ir_attachment", len(fnames))
    with OdooEnvironment(dbname) as env:
        for fname in fnames:
            env["ir.attachment"]._file_delete(fname)


def cleanup_modules(env):
    modules_to_uninstall = [
        i[2]["name"] for i in env["cleanup.purge.wizard.module"].find()
    ]

    # avoid to delete records from the model_record_to_keep modelscreated by the modules to uninstall
    logger.info(
        "Delete records from ir_model_data for models %s and modules %s",
        model_record_to_keep,
        modules_to_uninstall,
    )
    env.cr.execute(
        """Delete from ir_model_data where model in %s and module in %s""",
        (tuple(model_record_to_keep), tuple(modules_to_uninstall)),
    )
    logger.info("%d records deleted", env.cr.rowcount)

    # cleanup modules
    purger = env["cleanup.purge.wizard.module"].create({})
    purger.purge_all()
    purger.unlink()
    env.cr.commit()


def cleanup_models(env):
    logger.info("Cleanup models")
    purger = env["cleanup.purge.wizard.model"].create({})
    purger.purge_all()
    purger.unlink()
    env.cr.commit()


def cleanup_fields(env):
    logger.info("Cleanup fields")
    purger = env["cleanup.purge.wizard.field"].create({})
    purger.purge_all()
    purger.unlink()
    env.cr.commit()


def clenaup_columns(env):
    logger.info("Cleanup columns")
    purger = env["cleanup.purge.wizard.column"].create({})
    tables_to_keep = {"fetchmail_server", "ir_mail_server" "peppol_server"}
    for line in purger.purge_line_ids:
        model = env[line.model_id.model]
        if model._table in tables_to_keep:
            line.unlink()
    purger.purge_all()
    purger.unlink()
    env.cr.commit()


def cleanup_tables(env):
    logger.info("Cleanup fields")
    purger = env["cleanup.purge.wizard.table"].create({})
    tables_to_keep = {
        "endpoint_route",
        "pg_stat_statements",
        "pg_stat_statements_info",
        "product_price_history",
        "geography_columns",
        "geometry_columns",
        "spatial_ref_sys",
    }
    for line in purger.purge_line_ids:
        if line.name in tables_to_keep:
            line.unlink()
    purger.purge_all()
    purger.unlink()
    env.cr.commit()


def cleanup_data(env):
    logger.info("Cleanup data")
    purger = env["cleanup.purge.wizard.data"].create({})
    purger.purge_all()
    purger.unlink()
    env.cr.commit()


@contextmanager
def _view_stock_average_daily_sale_disabled(env):
    # drop view to allows safe delete of obsolete columns
    # and recreate it after
    view_name = "stock_average_daily_sale"
    env.cr.execute(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}")
    yield
    env["stock.average.daily.sale"].init()


if __name__ == "__main__":
    # initialize logging
    logging.basicConfig(level=logging.INFO)

    from click_odoo import OdooEnvironment

    connection_info = _connection_info_for(dbname)
    create_fk_index_ir_attachment(connection_info)
    delete_round_instance_mail_message(connection_info)
    # delete_round_instance_ir_attachment(connection_info)
    with OdooEnvironment(dbname) as env:
        cleanup_modules(env)
        cleanup_models(env)
        cleanup_fields(env)
        with _view_stock_average_daily_sale_disabled(env):
            clenaup_columns(env)
        cleanup_tables(env)
        cleanup_data(env)
