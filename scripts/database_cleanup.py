import importlib
import logging
import os
import sys
from contextlib import closing, contextmanager

from tqdm import tqdm

# fmt: off
os.environ["UPG_VALID_MODELS"] = ";".join([
    "report_journal_qweb_report_tax_line",
    'report_aged_partner_balance_qweb_account',
    'report_trial_balance_qweb',
    'report_qweb_abstract',
    'report_general_ledger_qweb_move_line',
    'report_aged_partner_balance_qweb',
    'report_aged_partner_balance_qweb_partner',
    'report_aged_partner_balance_qweb_line',
    'report_aged_partner_balance_qweb_move_line',
    'report_general_ledger_qweb',
    'report_general_ledger_qweb_account',
    'report_general_ledger_qweb_partner',
    'report_journal_qweb',
    'report_journal_qweb_journal',
    'report_journal_qweb_move',
    'report_journal_qweb_move_line',
    'report_journal_qweb_journal_tax_line',
    'report_open_items_qweb',
    'report_open_items_qweb_account',
    'report_open_items_qweb_partner',
    'report_open_items_qweb_move_line',
    'report_trial_balance_qweb_account',
    'report_trial_balance_qweb_partner',
])

if "odoo.upgrade" in sys.modules:
    importlib.reload(sys.modules["odoo.upgrade"])
# fmt: on

# flake8: noqa: E402
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, AsIs

import odoo
import odoo.sql_db
from odoo import models
from odoo.modules.module import get_module_path
from odoo.upgrade.util.fields import remove_field
from odoo.upgrade.util.models import remove_model
from odoo.upgrade.util.modules import column_exists, remove_module
from odoo.upgrade.util.pg import explode_query_range, parallel_execute, remove_column
from odoo.upgrade.util.records import remove_records

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


def cleanup_tables(cr):
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
    for table in tqdm(to_drop, desc="Ensuring tables dropped"):
        try:
            cr.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        except Exception as e:
            logger.warning(f"Failed to drop table {table}: {e}")


@contextmanager
def _view_stock_average_daily_sale_disabled(env):
    # drop view to allows safe delete of obsolete columns
    # and recreate it after
    view_name = "stock_average_daily_sale"
    env.cr.execute(f"DROP MATERIALIZED VIEW IF EXISTS {view_name}")
    yield
    env["stock.average.daily.sale"].init()


def clenup_round_instance_mail_message(cr):
    cr.execute("select 1 from mail_message where model='round.instance' limit 1")
    if not cr.fetchone():
        logger.info("No round.instance mail message to cleanup")
        return
    logger.info("Cleanup round instance child mail message")
    parallel_execute(
        cr,
        explode_query_range(
            cr,
            "delete from mail_message m where exists (select 1 from  mail_message mm where m.parent_id=mm.id and mm.model='round.instance') ",
            table="mail_message",
            alias="m",
        ),
    )
    logger.info("Cleanup round instance mail message")
    parallel_execute(
        cr,
        explode_query_range(
            cr,
            "delete from mail_message  WHERE model = 'round.instance'",
            table="mail_message",
        ),
    )


def cleanup_modules(cr):
    if column_exists(cr, "url_url", "model_id"):
        cr.execute("delete from url_url where model_id like 'shopinvader%';")
        cr.execute("alter table url_url drop column model_id;")
        cr.execute("alter table url_url drop column backend_id;")
    cr.execute("delete from mail_activity where user_id = 199;")
    cr.execute(
        "select name from ir_module_module where (to_buy = false or to_buy is null)"
    )
    modules = [i[0] for i in cr.fetchall()]
    modules = [m for m in modules if not get_module_path(m, display_warning=False)]
    # PRESERVE res_users, stock_picking_type deleclared in modules to remove
    if not modules:
        logger.info("No module to remove")
        return
    cr.execute(
        "DELETE FROM ir_model_data WHERE model in %s AND module in %s",
        (
            tuple(model_record_to_keep),
            tuple(modules),
        ),
    )
    # preserve product
    cr.execute(
        "DELETE FROM ir_model_data WHERE model in('product.template') AND module in %s",
        (tuple(modules),),
    )
    logger.info("Uninstall %d modules", len(modules))
    for module in tqdm(modules, desc="Removing modules"):
        # if module == "account_financial_report_qweb":
        #    continue
        tqdm.write(f"Currently removing module: {module}")
        remove_module(cr, module)
        cr.commit()


def cleanup_models(cr):
    models = [
        "connector.config.settings",
        "report_journal_qweb_report_tax_line",
        "stock.location.storage.type",
        "alc.document.prices.data",
        "report.report_alc_product_promotion_mailing",
        "base.action.rule.lead.test",
        "geoengine.vector.symbol",
        "aged.partner.balance.wizard",
        "report_aged_partner_balance_qweb_account",
        "report_trial_balance_qweb",
        "report_qweb_abstract",
        "alc.db.cleaner",
        "veterinary.group.user.wizard",
        "se.backend.elasticsearch",
        "report_general_ledger_qweb_move_line",
        "se.backend.spec.abstract",
        "procurement.order.compute.all",
        "account.financial.html.report.xml.export",
        "base.action.rule.line.test",
        "connector.checkpoint",
        "connector.checkpoint.review",
        "stock.pack.operation.lot",
        "bank.payment.line",
        "account.move.reverse",
        "journal.report.wizard",
        "report_aged_partner_balance_qweb",
        "report_aged_partner_balance_qweb_partner",
        "report_aged_partner_balance_qweb_line",
        "report_aged_partner_balance_qweb_move_line",
        "report_general_ledger_qweb",
        "report_general_ledger_qweb_account",
        "report_general_ledger_qweb_partner",
        "report_journal_qweb",
        "report_journal_qweb_journal",
        "report_journal_qweb_move",
        "report_journal_qweb_move_line",
        "report_journal_qweb_journal_tax_line",
        "report_open_items_qweb",
        "report_open_items_qweb_account",
        "report_open_items_qweb_partner",
        "report_open_items_qweb_move_line",
        "report_trial_balance_qweb_account",
        "report_trial_balance_qweb_partner",
        "stock.location.package.storage.type.rel",
        "stock.package.storage.type",
        "alc.average.daily.sale",
        "stock.picking.to.wave",
        "alc.eshop.news",
        "alc.eshop.snippet",
        "product.set.add",
        "x_bi_sql_view.location_occupation_rate",
        "x_bi_sql_view.products_by_location_and_storagetype",
        "x_bi_sql_view.average_daily_sale_6_months",
        "x_bi_sql_view.average_daily_sale_12_months",
    ]

    for model in tqdm(models, desc="Removing models"):
        tqdm.write(f"Currently removing model: {model}")
        remove_model(cr, model)
        cr.commit()


def cleanup_fields(cr, fields):
    if not fields:
        logger.info("No orphaned fields found")
        return
    for field in tqdm(fields, desc="Removing fields"):
        tqdm.write(f"Currently removing field: {field}")
        remove_field(cr, *field)


def collect_fields_to_remove(dbname):
    from click_odoo import OdooEnvironment

    fields = []
    with OdooEnvironment(dbname) as env:
        ignored_fields = [
            *models.MAGIC_COLUMNS,
            "display_name",
            models.BaseModel.CONCURRENCY_CHECK_FIELD,
        ]
        domain = [("state", "=", "base")]
        for field_id in env["ir.model.fields"].search(domain):
            if field_id.name in ignored_fields:
                continue
            model = env[field_id.model_id.model]
            if field_id.name not in model._fields.keys():
                fields.append((field_id.model_id.model, field_id.name))
    return fields


blacklist = {
    "wkf_instance": ["uid"],  # lp:1277899
    "res_users": ["password", "password_crypt", "totp_secret"],
    "res_partner": ["signup_token"],
}
tables_to_keep = {"fetchmail_server", "ir_mail_server" "peppol_server"}
columns_to_keep = {"is_delivered_by_alcyon", "elasticsearch_role"}


def get_orphaned_columns(env, model_pools):
    if model_pools[0]._table in tables_to_keep:
        return []
    columns = list(
        {
            column.name
            for model_pool in model_pools
            for column in model_pool._fields.values()
            if not (column.compute is not None and not column.store)
        }
    )
    columns = [
        *columns,
        *models.MAGIC_COLUMNS,
        *blacklist.get(model_pools[0]._table, []),
        *columns_to_keep,
    ]

    env.cr.execute(
        "SELECT a.attname FROM pg_class c, pg_attribute a "
        "WHERE c.relname=%s AND c.oid=a.attrelid AND a.attisdropped=False "
        "AND pg_catalog.format_type(a.atttypid, a.atttypmod) "
        "NOT IN ('cid', 'tid', 'oid', 'xid') "
        "AND a.attname NOT IN %s",
        (model_pools[0]._table, tuple(columns)),
    )
    return [column for column, in env.cr.fetchall() if column]


def collect_columns_to_remove(dbname):
    from click_odoo import OdooEnvironment

    columns = []
    with OdooEnvironment(dbname) as env:
        table2model = {}

        for model in env["ir.model"].search([]):
            if model.model not in env:
                continue
            model_pool = env[model.model]
            if not model_pool._auto:
                continue
            table2model.setdefault(model_pool._table, (model.id, []))[1].append(
                model_pool
            )

        for table, model_spec in table2model.items():
            for column in get_orphaned_columns(env, model_spec[1]):
                columns.append((table, column))
    return columns


def cleanup_column(cr, columns):
    if not columns:
        logger.info("No orphaned columns found")
        return
    for column in tqdm(columns, desc="Removing columns"):
        tqdm.write(f"Currently removing column: {column}")
        remove_column(cr, column[0], column[1])
        cr.commit()


def collect_orphaned_xml_ids(dbname):
    from click_odoo import OdooEnvironment

    with OdooEnvironment(dbname) as env:
        data_ids = []
        unknown_models = []
        env.cr.execute("""SELECT DISTINCT(model) FROM ir_model_data""")
        for (model,) in env.cr.fetchall():
            if not model:
                continue
            if model not in env:
                unknown_models.append(model)
                continue
            env.cr.execute(
                """
                SELECT id FROM ir_model_data
                WHERE model = %s
                AND res_id IS NOT NULL
                AND NOT EXISTS (
                    SELECT id FROM %s WHERE id=ir_model_data.res_id)
                """,
                (model, AsIs(env[model]._table)),
            )
            data_ids.extend(data_row for data_row, in env.cr.fetchall())
        data_ids += (
            env["ir.model.data"]
            .search(
                [
                    ("model", "in", unknown_models),
                ]
            )
            .ids
        )
        return data_ids


def cleanup_xml_ids(cr, data_ids):
    if not data_ids:
        logger.info("No orphaned xml ids found")
        return
    logger.info("Cleanup orphaned %d xml ids", len(data_ids))
    remove_records(cr, "ir.model.data", data_ids)
    cr.commit()


if __name__ == "__main__":
    # initialize logging
    logging.basicConfig(level=logging.INFO)

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
        conn = odoo.sql_db.db_connect(dbname)
        with closing(conn.cursor()) as cr:
            clenup_round_instance_mail_message(cr)
            cleanup_modules(cr)
            cleanup_models(cr)
        fields_to_remove = collect_fields_to_remove(dbname)
        with closing(conn.cursor()) as cr:
            cleanup_fields(cr, fields_to_remove)
        columns_to_remove = collect_columns_to_remove(dbname)
        with closing(conn.cursor()) as cr:
            cleanup_column(cr, columns_to_remove)
        data_ids_to_remove = collect_orphaned_xml_ids(dbname)
        with closing(conn.cursor()) as cr:
            cleanup_xml_ids(cr, data_ids_to_remove)
            cleanup_tables(cr)
