import logging
import os
from collections import defaultdict
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


def create_fk_index(connection_info, referenced_table, excluded_tables=None):
    # create the missing index for FK to referenced_table_name
    # to speed up the delete operation.
    if excluded_tables is None:
        excluded_tables = []
    conn = psycopg2.connect(**connection_info)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with closing(conn.cursor()) as cr:
        query = f"""
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
                    AND ccu.table_name = '{referenced_table}'
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
            if not has_index and referencing_table not in excluded_tables:
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
        max_workers=5,
    )


def delete_round_instance_ir_attachment(connection_info):
    conn = psycopg2.connect(**connection_info)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    ir_attachment_ids = []
    fnames = []
    with closing(conn.cursor()) as cr:
        cr.execute(
            """
            SELECT id, store_fname from ir_attachment
            WHERE res_model = 'round.instance'
            """
        )
        for i in cr.fetchall():
            ir_attachment_ids.append(i[0])
            fnames.append(i[1])
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


def cleanup_ir_model_data(connection_info):
    logger.info("Cleanup ir_model_data")
    conn = psycopg2.connect(**connection_info)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    # into ir_model_data we must find all the records defined for the
    # same model and res_id. If one of the record refers to a module
    # still installed we must delete the other records. If all the records
    # refers to a module installed we must keep them. If all the records
    # refers to a module not installed we must keep them too.
    # The goal is to avoid to remove records that are still used by the
    # installed modules when obsolete modules are uninstalled.
    sql = r"""
        with duplicates as (
            SELECT
                model, res_id
            FROM
                ir_model_data
            GROUP BY
                model, res_id
            HAVING
                COUNT(id) > 1
        )
        SELECT
            imd.id, imd.model, imd.res_id, imd.module, imd.name,
            (m.name is not null or imd.module like '\_\_%') as module_installed
        FROM
            ir_model_data imd
            join duplicates d on imd.model = d.model and imd.res_id = d.res_id
            left join ir_module_module m on imd.module = m.name and state = 'installed'
        ORDER BY
            imd.model, imd.res_id, module_installed;
    """
    with closing(conn.cursor()) as cr:
        cr.execute(sql)
        info_by_model_res_id = defaultdict(list)
        for id, model, res_id, module, name, module_installed in cr.fetchall():
            info_by_model_res_id[(model, res_id)].append(
                (id, module, name, module_installed)
            )
        for (model, res_id), info in info_by_model_res_id.items():
            if all(module_installed for _, _, _, module_installed in info):
                continue
            if all(not module_installed for _, _, _, module_installed in info):
                continue
            for id, module, name, module_installed in info:
                if module_installed:
                    continue
                logger.info(
                    "Delete ir_model_data %s.%s (%s - %s)", module, name, model, res_id
                )
                cr.execute("DELETE FROM ir_model_data WHERE id = %s", (id,))


def _do_purge_lines(purger):
    total = len(purger.purge_line_ids)
    actual = 0
    for line in purger.purge_line_ids:
        actual += 1
        logger.info("Purge %s: %d/%d %s", purger._name, actual, total, line.name)
        line.purge()
        line.env.cr.commit()
    purger.unlink()
    env.cr.commit()


def cleanup_modules(env):
    modules_to_uninstall = [
        i[2]["name"] for i in env["cleanup.purge.wizard.module"].find()
    ]

    # avoid to delete records from the model_record_to_keep modelscreated by the modules to uninstall
    logger.info(
        "Delete records from ir_model_data for models not in %s and modules %s",
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
    _do_purge_lines(purger)


def cleanup_models(env):
    logger.info("Cleanup models")
    purger = env["cleanup.purge.wizard.model"].create({})
    _do_purge_lines(purger)


def cleanup_fields(env):
    logger.info("Cleanup fields")
    purger = env["cleanup.purge.wizard.field"].create({})
    _do_purge_lines(purger)


def clenaup_columns(env):
    logger.info("Cleanup columns")
    purger = env["cleanup.purge.wizard.column"].create({})
    tables_to_keep = {"fetchmail_server", "ir_mail_server" "peppol_server"}
    for line in purger.purge_line_ids:
        model = env[line.model_id.model]
        if model._table in tables_to_keep:
            line.unlink()
    _do_purge_lines(purger)


def cleanup_tables(env):
    logger.info("Cleanup tables")
    to_drop = [
        "account_mass_reconcile_method",
        "mass_reconcile_history",
        "aged_partner_balance_wizard_res_partner_rel",
        "alc_delivery_resource_round_template_rel",
        "alc_delivery_resource_round_instance_rel",
        "alc_eshop_news_res_lang_rel",
        "alc_eshop_snippet_res_lang_rel",
        "attribute_set_completeness_product_template_rel",
        "bi_sql_view_field",
        "bi_sql_view_res_groups_rel",
        "bi_sql_view_res_users_rel",
        "change_lot_line",
        "connector_checkpoint_review_rel",
        "credit_control_communication_credit_control_line_rel",
        "credit_control_emailer_credit_control_line_rel",
        "credit_control_policy_changer",
        "credit_control_policy_level",
        "credit_control_line_credit_control_printer_rel",
        "credit_control_line_credit_control_marker_rel",
        "credit_control_policy_credit_control_run_rel",
        "cron_delivery_plan_round_tag_rel",
        "esb_backend_timestamp",
        "generate_voice_identifier_stock_production_lot_rel",
        "mass_reconcile_advanced_partner_res_partner_rel",
        "mass_reconcile_advanced_ref_res_partner_rel",
        "mass_reconcile_simple_name_res_partner_rel",
        "mass_reconcile_simple_partner_res_partner_rel",
        "mass_reconcile_simple_reference_res_partner_rel",
        "partner_archive_new_partner_wizard_sale_order_rel",
        "partner_archive_new_partner_wizard_stock_picking_rel",
        "product_filter_shopinvader_backend_rel",
        "product_image_relation_product_product_rel",
        "product_media_relation_product_product_rel",
        "product_set_add_product_set_line_rel",
        "round_template",
        "shape_file_import_wizard",
        "report_aged_partner_balance_qweb_account",
        "report_general_ledger_qweb_account",
        "report_journal_qweb_journal",
        "report_journal_qweb_journal_tax_line",
        "report_journal_qweb_move_line",
        "report_journal_qweb_move",
        "report_journal_qweb_report_tax_line",
        "report_open_items_qweb_account",
        "report_trial_balance_qweb_account",
        "report_aged_partner_balance_qweb_res_partner_rel",
        "report_general_ledger_qweb_res_partner_rel",
        "report_open_items_qweb_res_partner_rel",
        "report_trial_balance_qweb_res_partner_rel",
        "round_instance_customer",
        "round_instance_round_itinerary_rel",
        "round_instance_round_tag_rel",
        "round_instance_stock_picking_wave_rel",
        "round_instance_picking_state",
        "round_itinerary_position",
        "round_itinerary_import",
        "round_wizard_makeplan",
        "round_itinerary_round_template_rel",
        "round_itinerary_position_round_tag_rel",
        "round_template_round_template_version_rel",
        "shopinvader_category",
        "shopinvader_category_binding_wizard",
        "shopinvader_notification",
        "shopinvader_partner",
        "shopinvader_partner_binding",
        "shopinvader_product",
        "shopinvader_variant_binding_wizard",
        "shopinvader_backend_stock_warehouse_rel",
        "shopinvader_category_shopinvader_category_unbinding_wizard_rel",
        "shopinvader_partner_binding_line",
        "shopinvader_variant_unbind_wizard_rel",
        "stock_pack_operation_skip_lot",
        "storage_file",
        "wizard_update_charts_accounts_tax",
        "wizard_update_charts_accounts_account",
        "wizard_update_charts_accounts_fiscal_position",
        "wizard_update_charts_fp_fields_rel",
        "wizard_update_charts_tax_fields_rel",
    ]
    logger.info("Drop %d tables", len(to_drop))
    for table in to_drop:
        env.cr.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
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
    _do_purge_lines(purger)


def cleanup_data(env):
    logger.info("Cleanup data")
    purger = env["cleanup.purge.wizard.data"].create({})
    _do_purge_lines(purger)


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
    # cleanup_ir_model_data(connection_info)
    create_fk_index(connection_info, "ir_attachment")
    create_fk_index(
        connection_info,
        "mail_message",
        [
            "mail_compose_message",
            "rating_rating",
            "mail_channel_member",
            "mail_group_message",
            "mail_link_preview",
            "mail_message_reaction",
            "mail_message_res_partner_starred_rel",
            "mail_message_schedule",
            "mail_resend_message",
            "rating_rating",
            "sms_sms",
            "sms_resend",
            "snailmail_letter",
            "snailmail_letter_format_error",
        ],
    )
    if True:
        delete_round_instance_mail_message(connection_info)
        delete_round_instance_ir_attachment(connection_info)
    if True:
        with OdooEnvironment(dbname) as env:
            cleanup_modules(env)
            cleanup_models(env)
            cleanup_fields(env)
            with _view_stock_average_daily_sale_disabled(env):
                clenaup_columns(env)
            cleanup_tables(env)
            cleanup_data(env)
