import functools
import logging

from click_odoo.env import OdooEnvironment
from openupgradelib import openupgrade
from setuptools_odoo import base_addons

from odoo.tools import parse_version

from odoo.addons.base_geoengine.geo_db import init_postgis

from . import VERSION
from .call import check_call
from .dbtools import copydb, copytable, cursor, psql_file, recover_columns, ref_id
from .migration import MigrationScriptsManager

DB_10_SRC_NOT_CLEANED = "odoo-alcyon-prod"  # the db with geo fields..
DB_16_MIG = "alcyon-migrated"
DB_16_POSTMIG = "alcyon-16-postmig"
DB_16_FINAL = "alcyon-16-final"
DB_16_RECETTE = "alcyon-16-recette"

tasks = []

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

_logger = logging.getLogger(__name__)


# get version from alc_all addons
def get_version():
    """Get the version of the alc_all module from the database."""
    try:
        with cursor(DB_16_POSTMIG) as cr:
            cr.execute(
                "SELECT latest_version FROM ir_module_module WHERE name = 'alc_all'"
            )
            return cr.fetchone()[0]
    except Exception:
        return "10.0.0.0.0"


CURRENT_VERSION = VERSION or get_version()
PARSED_CURRENT_VERSION = parse_version(CURRENT_VERSION)


def task(version=None):
    """Decorator that register the function into the tasks list.

    if the version is None or the version is less than the current version.
    """

    def f(func):
        if version is None or parse_version(version) > PARSED_CURRENT_VERSION:
            tasks.append((func.__name__, func))

    return f


def _register_migration_scripts_in_tasks(prefix):
    """Register migrate method from modules into the migrations module.

    where modules are found by the fsmatch_pattern.

    :param prefix: The prefix of the modules to register.
    """
    migration_manager = MigrationScriptsManager(prefix, CURRENT_VERSION)
    for name, callable_def in migration_manager.callable_defs.items():

        def wrapped(callable_def=callable_def):
            # define attributes into the locals context
            # required by the openupgrade.migrate method
            # get ModuleSpec from module
            locals().update(
                {
                    "stage": callable_def.stage,
                    "pkg": callable_def.spec,
                    "pyfile": callable_def.spec.name + ".py",
                }
            )
            # disable all logging output
            try:
                logging_config = logging.getLogger().getEffectiveLevel()
                logging.disable(logging.CRITICAL)
                if prefix == "pre-":
                    # Don't load environment as not already migrated to
                    # last version
                    with cursor(DB_16_POSTMIG) as cr:
                        logging.disable(logging.NOTSET)
                        logging.getLogger().setLevel(logging_config)
                        callable_def.callable(cr, version=CURRENT_VERSION)
                elif prefix == "post-":
                    with OdooEnvironment(DB_16_POSTMIG) as env:
                        logging.disable(logging.NOTSET)
                        logging.getLogger().setLevel(logging_config)
                        callable_def.callable(env.cr, version=CURRENT_VERSION)

            finally:
                # Restore the original logging configuration
                logging.disable(logging.NOTSET)
                logging.getLogger().setLevel(logging_config)

        tasks.append((name, functools.partial(wrapped, callable_def=callable_def)))


@task("16.0.1.0.0")
def copydb_16_postmig():
    copydb(DB_16_MIG, DB_16_POSTMIG)


@task("16.0.1.0.0")
def ensure_postgis():
    with cursor(DB_16_POSTMIG) as cr:
        init_postgis(cr)


@task("16.0.1.0.0")
def cleanup_geoengine_layers():
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            DELETE FROM geoengine_vector_layer;
        """
        openupgrade.logged_query(cr, query)
        query = """
            DELETE FROM geoengine_raster_layer;
        """
        openupgrade.logged_query(cr, query)


@task("16.0.1.0.0")
def delete_uninstallable_xml_ids():
    """Delete menus, filters, record rules from uninstallable modules."""
    # TODO: this could be done unconditionally for all these records?
    with cursor(DB_16_POSTMIG) as cr:
        for model, table, fk_column in (
            ("report.layout", "report_layout", None),
            ("ir.ui.view", "ir_ui_view", "inherit_id"),
            ("ir.filters", "ir_filters", None),
            ("ir.ui.menu", "ir_ui_menu", "parent_id"),
            ("ir.rule", "ir_rule", None),
            ("ir.cron", "ir_cron", None),
            ("ir.actions.todo", "ir_actions_todo", None),
            ("ir.actions.server", "ir_act_server", None),
            ("ir.actions.report", "ir_act_report_xml", None),
            ("ir.actions.client", "ir_act_client", None),
            ("ir.actions.act_window", "ir_act_window", None),
        ):
            # we delete the records from the table. For each table to delete,
            # we get the name of the column that is the foreign key to the
            # same table. We ensure that the record is not referenced by
            # another record.
            if fk_column:
                update = ""
                if table == "ir_ui_view":
                    update = ", mode='todelete'"
                query = f"""
                    UPDATE {table} set {fk_column}=NULL {update} WHERE {fk_column} IN (
                            select res_id from ir_model_data imd
                            left join ir_module_module imm on imm.name=imd.module
                            where (imm.state != 'installed' or imm.latest_version NOT LIKE '16.%') and model='{model}'
                        )
                    """
                cr.execute(query)
                print("Updated", cr.rowcount, f"from {table}")

            query = f"""
                delete from {table}
                where id in (
                    select res_id from ir_model_data imd
                    left join ir_module_module imm on imm.name=imd.module
                    where (imm.state != 'installed' or imm.latest_version NOT LIKE '16.%') and model='{model}'
                )
                """
            cr.execute(query)
            print("deleted", cr.rowcount, f"from {table}")

            if model.startswith("ir.actions."):
                query = f"""
                    delete from ir_actions
                    where id in (
                        select res_id from ir_model_data imd
                        left join ir_module_module imm on imm.name=imd.module
                        where (imm.state != 'installed' or imm.latest_version NOT LIKE '16.%') and model='{model}'
                    )
                    """
                cr.execute(query)
                print("deleted", cr.rowcount, "from ir_actions")

            query = f"""
                delete from ir_model_data
                where model='{model}'
                and module in (
                    select name from ir_module_module where (state != 'installed' or latest_version NOT LIKE '16.%')
                )
                """
            cr.execute(query)
            print("deleted", cr.rowcount, "from ir_model_data")


@task("16.0.2.1.3")
def delete_custom_filters():
    """Delete custom filters from the ir.filters table."""
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            delete from ir_filters
            where id not in (
                select res_id from ir_model_data where model='ir.filters'
            )
            """
        cr.execute(query)
        print("deleted", cr.rowcount, "from ir_filters")


@task("16.0.1.0.0")
def cleanup_assets():
    query = """
        DELETE FROM ir_asset ia
        WHERE EXISTS(
            SELECT
                True
            FROM
                ir_module_module imm
            WHERE
                ia.name LIKE CONCAT(imm.name, '.%')
                AND imm.state != 'installed' or imm.latest_version NOT LIKE '16.%'
        );
        """
    with cursor(DB_16_POSTMIG) as cr:
        cr.execute(query)
        print("deleted", cr.rowcount, "from ir_asset")


@task("16.0.1.0.0")
def clean_vlb_content():
    # Odoo gives us a migration DB with a zero quantity quant in VLB
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            DELETE FROM stock_quant
                WHERE location_id = 11
                AND quantity = 0
        """
        openupgrade.logged_query(cr, query)


@task("16.0.1.0.0")
def cleanup_sale_typology_domain():
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            update ir_act_window iaw
            set domain = Null
            where domain like '%typology%'
        """
        cr.execute(query)
        print("updated", cr.rowcount, "from ir_act_window for sale typology domain")


@task("16.0.1.0.0")
def cleanup_non_odoo_views():
    with cursor(DB_16_POSTMIG) as cr:
        odoo_addons = tuple([i for i in base_addons.odoo16 if i])
        query = """
            UPDATE ir_ui_view set mode='todelete', inherit_id = NULL where inherit_id IN (
                SELECT res_id FROM ir_model_data
                    WHERE module NOT IN %(modules)s
                    AND model='ir.ui.view'
            );"""
        openupgrade.logged_query(cr, query, {"modules": odoo_addons})
        query = """
            DELETE FROM ir_ui_view WHERE id IN (
                SELECT res_id FROM ir_model_data
                    WHERE module NOT IN %(modules)s
                    AND model='ir.ui.view'
                );"""
        openupgrade.logged_query(cr, query, {"modules": odoo_addons})
        query = """
            DELETE FROM ir_ui_view WHERE mode='todelete';
            """
        openupgrade.logged_query(cr, query)
        query = """
            DELETE FROM ir_model_data
            WHERE module NOT IN %(modules)s AND model='ir.ui.view';
        """
        openupgrade.logged_query(cr, query, {"modules": odoo_addons})


@task("16.0.1.0.0")
def clean_veterinary():
    query = """
        delete from res_partner_veterinary_group_rel
            WHERE NOT EXISTS
                (SELECT 1 FROM res_partner WHERE id = res_partner_id);
    """
    with cursor(DB_16_POSTMIG) as cr:
        openupgrade.logged_query(cr, query)


@task("16.0.1.0.0")
def cleanup_stock_quant_package():
    psql_file(
        DB_16_POSTMIG,
        "psql/cleanup-stock-quant-package-product-packaging-id-fkey.sql",
    )


@task("16.0.1.0.0")
def migrate_account_payment_mode():
    with cursor(DB_16_POSTMIG) as cr:
        rule_id = ref_id(cr, "account_payment_mode.account_payment_mode_company_rule")
        query = "update ir_rule set domain_force = %s where id = %s"
        openupgrade.logged_query(
            cr,
            query,
            (
                "['|',('company_id','=',False),('company_id','in',company_ids)]",
                rule_id,
            ),
        )


@task("16.0.1.0.0")
def migrate_account_payment_partner():
    # TODO verify number of move_line with a payment_mode_id
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            UPDATE account_payment_mode
            SET show_bank_account_from_journal = true
            WHERE bank_account_link = 'fixed'
        """
        openupgrade.logged_query(cr, query)
        query = """
            UPDATE account_move am
            SET payment_mode_id = ai.payment_mode_id
            FROM account_invoice ai
            WHERE ai.number = am.name and ai.payment_mode_id IS NOT NULL"""
        openupgrade.logged_query(cr, query)
        query = """
            UPDATE account_move_line aml
            SET payment_mode_id = am.payment_mode_id
            FROM account_move am
            WHERE am.id = aml.move_id
                AND am.move_type IN ('out_invoice', 'out_refund', 'in_invoice', 'in_refund')
                AND aml.account_type in ('liability_payable', 'asset_receivable')
                AND aml.payment_mode_id IS NULL AND am.payment_mode_id IS NOT NULL"""
        openupgrade.logged_query(cr, query)


@task("16.0.1.0.0")
def cleanup_queue_job():
    psql_file(DB_16_POSTMIG, "psql/cleanup-queue-job.sql")


@task("16.0.1.0.0")
def migrate_product_packaging_level():
    with cursor(DB_16_POSTMIG) as cr:
        # Former version of the module is present
        tables = [("product_packaging_type", "product_packaging_level")]
        openupgrade.rename_tables(cr, tables)
        models = [("product.packaging.type", "product.packaging.level")]
        openupgrade.rename_models(cr, models)
        fields = [
            (
                "product.packaging",
                "product_packaging",
                "packaging_level_id",
                "packaging_level_id",
            )
        ]
        openupgrade.rename_fields(cr, fields, no_deep=True)

        modules = [("product_packaging_type", "product_packaging_level")]
        openupgrade.update_module_names(cr, modules, merge_modules=True)
        openupgrade.rename_xmlids(
            cr,
            [
                (
                    "product_packaging_level.product_packaging_type_default",
                    "product_packaging_level.product_packaging_level_default",
                )
            ],
        )


@task("16.0.1.0.0")
def cleanup_partner_discount_rel():
    psql_file(DB_16_POSTMIG, "psql/cleanup-partner-discount-rel.sql")


@task("16.0.1.0.0")
def fix_product_packaging_data_and_structure():
    recover_columns(DB_10_SRC_NOT_CLEANED, DB_16_POSTMIG, "product_packaging")


@task("16.0.1.0.0")
def recover_partner_info():
    recover_columns(
        DB_10_SRC_NOT_CLEANED,
        DB_16_POSTMIG,
        "res_partner",
        {"geo_point": "geometry(Point, 3857)", "opt_out": "boolean"},
    )


@task("16.0.1.0.0")
def recover_round_template_geo_polygon_shape():
    recover_columns(
        DB_10_SRC_NOT_CLEANED,
        DB_16_POSTMIG,
        "round_template",
        {"geo_polygon_shape": "geometry(MultiPolygon,3857)"},
    )


@task("16.0.1.0.0")
def declare_alc_product_category_data_module_as_installed():
    with cursor(DB_16_POSTMIG) as cr:
        # we first check if the record exists in the database
        query = """
               SELECT id
               FROM ir_module_module
               WHERE name = 'alc_product_category_data'
               """
        cr.execute(query)
        if cr.fetchone():
            return
        # create a new ir_module_module record for the product_category_data module
        # by copying the data from the specific_data module
        query = """
            INSERT INTO ir_module_module
            (name, state, author, website, license, shortdesc, description, auto_install, latest_version, sequence, category_id, icon, create_uid, create_date, write_uid, write_date)
            SELECT 'alc_product_category_data', 'to upgrade', author, website, license, shortdesc, description, auto_install, '10.0.1.0.0', sequence, category_id, icon, create_uid, create_date, write_uid, write_date
            FROM ir_module_module
            WHERE name = 'specific_data'
            """
        openupgrade.logged_query(cr, query)

        # declare xml ids for product.category
        # as no update
        openupgrade.logged_query(
            cr,
            """
            UPDATE ir_model_data
            SET noupdate=True
            WHERE module='specific_data'
            AND model='product.category'
        """,
        )


@task("16.0.1.0.0")
def fix_account_tax_one_vat():
    with cursor(DB_16_POSTMIG) as cr:
        if not openupgrade.column_exists(cr, "account_tax", "is_vat"):
            query = """
            Alter table account_tax
            add column is_vat boolean;
            """
            openupgrade.logged_query(cr, query)
        query = """
            update account_tax
            set is_vat = true
            where tax_group_id = (select id from ir_model_data where name = 'vat_tax_group')
            """
        openupgrade.logged_query(cr, query)
        # remove old xmlid account_tax_one_vat.vat_tax_group
        query = """
            delete from ir_model_data
            where name = 'vat_tax_group'
            and module = 'account_tax_one_vat'
            """
        openupgrade.logged_query(cr, query)


@task("16.0.1.0.0")
def drop_materialized_views():
    with cursor(DB_16_POSTMIG) as cr:
        query = """
                SELECT matviewname
                FROM pg_matviews
                """
        openupgrade.logged_query(cr, query)
        materialized_views = [row[0] for row in cr.fetchall()]
        # drop materialized views
        for materialized_view in materialized_views:
            query = f"""
                    DROP MATERIALIZED VIEW IF EXISTS {materialized_view} CASCADE
                    """
            openupgrade.logged_query(cr, query)


@task("16.0.2.3.12")
def restore_account_analytic_tag_xmlids():
    """The account_analytic_tag xmlids are dropped during the migration process so.

    we need to recover them as they are heavily used in mis_builder reports
    """

    with cursor(DB_10_SRC_NOT_CLEANED) as cr:
        query = """
                SELECT noupdate, name, module, model, res_id
                FROM ir_model_data
                WHERE model like 'account.analytic.tag'
                """
        openupgrade.logged_query(cr, query)
        ana_tags = cr.fetchall()
    with cursor(DB_16_POSTMIG) as cr:
        query = """
                INSERT INTO ir_model_data(noupdate, name, module, model, res_id)
                VALUES (%s, %s, %s, %s, %s)
                """
        for ana_tag in ana_tags:
            openupgrade.logged_query(cr, query, ana_tag)


@task("16.0.2.3.12")
def recover_account_analytyc_tag_ids():
    # copy table account_analytic_account_tag_rel from db10 to db16
    table = "account_analytic_account_tag_rel"
    copytable(DB_10_SRC_NOT_CLEANED, DB_16_POSTMIG, table)


@task("16.0.2.5.2")
def recover_invoices_without_move():
    """
    Invoices with amount == 0 have no account move generated.

    They are paid.

    During migration, Odoo creates a new account_move but does not
    validate it - stays as draft.

    Collect all these invoices from account_invoice table v10 and
    set name and state
    """

    def __build_dict(cr, row):
        return {d.name: row[i] for i, d in enumerate(cr.description)}

    query = """
        SELECT id, name
            FROM account_invoice
            WHERE state = 'paid' AND move_id IS NULL
    """
    with cursor(DB_10_SRC_NOT_CLEANED) as cr:
        openupgrade.logged_query(cr, query)
        zero_invoices = [__build_dict(cr, row) for row in cr.fetchall()]
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            UPDATE account_move
                SET name = %(name)s, state = 'posted', payment_state = 'paid'
                WHERE id = (SELECT move_id FROM account_invoice WHERE id = %(id)s)
                AND state = 'draft';
        """
        for zero_invoice in zero_invoices:
            openupgrade.logged_query(cr, query, zero_invoice)


_register_migration_scripts_in_tasks("pre-")


@task("16.0.1.0.0")
def uninstallable_uninstalled():
    check_call(
        [
            "click-odoo",
            "-d",
            DB_16_POSTMIG,
            "click-odoo/unavailable-uninstallable.py",
        ]
    )


@task()
def cleanup_indexes():
    """Removes all existing indexes to let odoo recreate only the one defined.

    by the installed addons
    """
    query = """
        select format('DROP INDEX IF EXISTS %I.%I CASCADE;', s.nspname, i.relname) as drop_statement
            from pg_index idx
                join pg_class i on i.oid = idx.indexrelid
                join pg_class t on t.oid = idx.indrelid
                join pg_namespace s on i.relnamespace = s.oid
                left join pg_constraint c on c.conindid = i.oid
            where s.nspname  not in ('pg_catalog', 'pg_toast', 'topology')
                and not idx.indisprimary
                and c.conname is null;
    """
    with cursor(DB_16_POSTMIG) as cr:
        cr.execute(query)
        drop_index_queries = [row[0] for row in cr.fetchall()]
        total = len(drop_index_queries)
        _logger.info("Start dropping %d indexes", len(drop_index_queries))
        count = 0
        for drop_query in drop_index_queries:
            count += 1
            _logger.info("Drop index %d of %s", count, total)
            openupgrade.logged_query(cr, drop_query)


@task()
def click_odoo_update():
    check_call(["click-odoo-update", "-d", DB_16_POSTMIG, "--i18n-overwrite"])


_register_migration_scripts_in_tasks("post-")


@task("16.0.2.5.3")
def recover_intrastat():
    """
    Recover intrastat codes from v10 as they have been deleted by Odoo on.

    categories.

    Set them to specific fields (both categories and products).
    """

    def __build_dict(cr, row):
        return {"id": row[0], "intrastat_id": row[1]}

    query = """
        SELECT pc.id, ric.name
            FROM product_category pc JOIN report_intrastat_code ric ON pc.intrastat_id = ric.id
            WHERE intrastat_id IS NOT NULL
    """
    with cursor(DB_10_SRC_NOT_CLEANED) as cr:
        openupgrade.logged_query(cr, query)
        categories = [__build_dict(cr, row) for row in cr.fetchall()]

    with OdooEnvironment(DB_16_POSTMIG) as env:
        query = """
            UPDATE product_category
                SET specific_intrastat_code_id = (SELECT id FROM account_intrastat_code WHERE code = %(intrastat_id)s ORDER BY id LIMIT 1)
                WHERE id = %(id)s;
        """
        env.cr.executemany(query, categories)

    query = """
        SELECT pp.id AS id, ric.name AS intrastat_code
            FROM product_product pp JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN report_intrastat_code ric ON pt.intrastat_id = ric.id
            WHERE pt.intrastat_id IS NOT NULL
    """
    with cursor(DB_10_SRC_NOT_CLEANED) as cr:
        openupgrade.logged_query(cr, query)
        categories = [__build_dict(cr, row) for row in cr.fetchall()]

    with OdooEnvironment(DB_16_POSTMIG) as env:
        query = """
            UPDATE product_product
                SET specific_intrastat_code_id = (SELECT id FROM account_intrastat_code WHERE code = %(intrastat_id)s ORDER BY id LIMIT 1)
                WHERE id = %(id)s;
        """
        env.cr.executemany(query, categories)


@task("16.0.2.5.3")
def update_intrastat_code():
    check_call(
        [
            "click-odoo",
            "-d",
            DB_16_POSTMIG,
            "click-odoo/update-intrastat-code.py",
        ]
    )


@task("16.0.1.0.0")
def copydb_16_before_big_remove():
    copydb(DB_16_POSTMIG, DB_16_FINAL)


@task()
def set_modules_to_remove():
    """
    Set modules to remove as using the action is not available.

    as modules are not loaded in registry
    """
    # TODO: Re-activate this one as soon as all dependencies are migrated
    # or deleted. Indeed, some modules are still installed (in 10 version)
    # and pull some removed modules - so, the update will install them
    modules_list = [
        "alc_internal_stock_quant_package",
        "alc_product_picking_zone",
        "alc_product_storage_type_tracking",
        "alc_product_uom_updatable",
        "alc_stock_location_content_relocation",
        "alc_stock_move_operation",
        "alc_stock_pack_operation_audit",
        "alc_stock_picking_no_pack_in_pack",
        "alc_stock_picking_number_package",
        "alc_stock_picking_package",
        "alc_stock_picking_policy_block",
        "alc_stock_picking_wave_release_pickings",
        "alc_stock_picking_type_locking",
        "alc_stock_quant_package_delivery",
        "alc_stock_quant_package_nbr",
        "alc_stock_receive_lot_inputmask",
        "alc_stock_putaway",
        "alc_stock_storage_type_fixed_location",
        "base_geolocalize_openstreetmap",  # Replaced by STD
        "base_vat_sanitized",  # Replaced by STD
        "delivery_carrier_label_gls_server_env",
        "grid",
        "partner_delivery",
        "partner_helper",
        "portal_sale",
        "portal_stock",
        "procurement_sale",
        "product_packaging_barcode",
        "product_price_import",
        "purchase_prepaid",
        "purchase_unlink_cancelop",
        "purchase_update_procurement_qty",
        "specific_zetes",
        "stock_delivery_note",
        "stock_expired",
        "stock_inventory_controller",
        "stock_inventory_products",
        "stock_location",
        "stock_location_act_as_view",
        "stock_location_notranslate",
        "stock_location_report",
        "stock_operation_cleaner",
        "stock_operation_recompute",
        "stock_production_lot_expiry",
        "stock_reassign_auto",
        "stock_picking_assignment",
        "stock_picking_backorder",
        "stock_picking_fillwithstock",
        "stock_picking_show_backorder",
        "stock_putaway_defaultfixedlocation",
        "stock_putaway_route",
        "stock_quant_bylocation",
        "base_cached_xmlid",
        "specific_data",
        "pricelist_discount",
        "stock_picking_subcode",  # replaced by stock_move_picking_type_origin
        "purchase_open_qty",
        "stock_mts_mto_rule",
        "stock_disable_force_availability_button",
        "alc_sale_channel_stock_move",
        "sale_order_price_recalculation",
        "alc_sale_order_price_recalculation",  # merged into alc_pricelist_discount
        "sale_delay",  # replaced by alc_sale_auto_confirm_max_delay
        "sale_internal_confirmation_mail",  # replaced by alc_sale_internal_confirmation_mail
        "materialized_view_mixin",  # replaced by alc_materialized_view_mixin
        "alc_geo_delivery_rounds",  # replaced by alc_stock_release_channel_tag & alc_stock_release_channel_import
        "alc_delivery_rounds_operator",  # replaced by alc_stock_release_channel_user
        "sale_cancel_remaining",  # replaced by sale_order_line_cancel
        "alc_delivery_rounds_close_pickings_by_zone",  # replaced by alc_stock_release_channel_pick_allowed
        "alc_delivery_rounds_allatonce_assignment",
        "alc_delivery_rounds_partner_geolocalize",
        "web_decimal_numpad_dot",
        "alc_stock_picking_batch_delivery_rounds",  # replaced by alc_stock_release_channel_picking_batch_creation
        "specific_shipping_costs",  # replaced by alc_shipping_fee
        "alc_b2c_to_magento",
        "base_suspend_security",
        "alc_reception_pharmacy_geo_delivery_rounds",  # replaced by alc_reception_pharmacy_geo_release_channel
        "specific_security",
        "speedy_views",
        "alc_stock_receive_frigo",
        "alc_delivery_rounds_gls",  # replaced by alc_stock_release_channel_user_gls & alc_stock_release_channel_deliver_gls
        "alc_delivery_rounds_assign_blocking",  # replaced by alc_stock_release_channel_assign_blocking_unavailable_product
        "alc_delivery_rounds_assign_blocking_unavailable_product",  # replaced by alc_stock_release_channel_assign_blocking_unavailable_product
        "alc_sale_product_expected_receipt_date",  # replaced by alc_sale_order_line_forecast_expected_date
        "alc_sale_product_qty_available_to_promise",  # useless
        "web_widget_domain_v11",
        "web_tree_image",
        "web_export_view",
        "web_readonly_bypass",
        "web_cache_name_get",
        "monitoring_status",
        "logging_json",
        "base_search_custom_field_filter",
        "base_import_async",
        "web_widget_color",
        "web_widget_inputmask",
        "web_m2x_options",
        "web_widget_many2many_tags_multi_selection",
        "mass_editing",  # replaced by server_action_mass_edit
        "alce_l10n_be_reports",
        "account_invoice_merge_purchase",
        "account_invoice_force_number",
        "account_group",
        "account_chart_update",
        "account_invoice_merge_attachment",
        "account_invoice_merge",
        "account_cutoff_accrual_base",
        "account_cutoff_accrual_return",
        "account_type_menu",
        "account_financial_report_date_range",
        "account_move_line_report_xls",
        "account_mass_reconcile_partner",
        "account_mass_reconcile",
        "alc_shopfloor",  # replaced by OCA module shopfloor
        "alc_shopfloor_mobile",  # replaced by shopfloor_mobile
        "alc_shopfloor_cluster_picking",  # replaced by shopfloor_batch_automatic_creation
        "alc_shopfloor_rest_log",  # replaced by shopfloor_rest_log
        "alc_shopfloor_delivery_rounds",  # replaced by alc_shopfloor_stock_release_channel
        "alc_shopfloor_packing",  # replaced by shopfloor_packing
        "alc_shopfloor_mobile_packing",  # replaced by shopfloor_mobile_packing
        "alc_shopfloor_unassign_wave",  # replaced by shopfloor
        "alc_shopfloor_location_content_relocation",  # included in base module
        "alc_shopfloor_mobile_change_pack_lot_back_button",  # included in base module
        "alc_shopfloor_app",  # replaced by alc_app_shopfloor
        "alc_shopfloor_assignation_issue_message",  # included in base module
        "analytic_tag_dimension",
        "analytic_tag_dimension_purchase_warning",
        "analytic_tag_dimension_sale_warning",
        "alc_shopfloor_location_info",  # included in base module
        "alc_shopfloor_mobile_stock_refill",  # included in base module
        "document_unindex_content",
        "alc_stock_put_remaining_to_reserve",
        "account_invoice_payment_report",  # replaced by STD
        "account_payment_order_background",
        "storage_backend",
        "storage_backend_s3",
        "storage_thumbnail",
        "storage_media",
        "storage_media_product",
        "storage_image",
        "storage_image_product",
        "storage_file",
        "alc_storage_file_lang",
        "alc_storage_media_lang",
        "alc_storage_media_product",
        "alc_product_brand_image",
        "alc_product_consolidated_price",
        "specific_cutoff",  # replaced by alc_account_invoice_accrual & account_cutoff_accrual_sale & account_cutoff_accrual_purchase
        "stock_valuation",  # replaced by STD
        "alc_product_packaging_stock_reserve",
        "account_analytic_no_lines",
        "account_credit_control",
        "alcyon_credit_control",
        "mixin_file_id",
        "mixin_image_id",
        "specific_report",
        "shopinvader_search_engine_update_product",
        "shopinvader_search_engine_update_media",
        "shopinvader_search_engine_update_links",
        "alc_eshop_product_image_sequence",
        "alc_eshop_classifieds_service",  # renamed to alc_eshop_api_classifieds
        "alc_eshop_sale_statistic",  # renamed to alc_eshop_api_sale_statistic
        "alc_registration_eshop_service",  # renamed to alc_eshop_api_registration
        "elasticsearch_search",
        "alc_eshop_ads_elasticsearch",  # renamed to alc_eshop_search_engine_ads
        "alc_eshop_info_banner_elasticsearch",  # renamed to alc_eshop_search_engine_info_banner
        "authenticated_partner_mixin",  # renamed to shopinvader_restapi
        "alc_documents_eshop_services",  # renamed to alc_eshop_api_documents
        "alc_eshop_user_migration",
        "alc_eshop_services_catalog",  # renamed to alc_eshop_api_catalog
        "alc_eshop_services_discounts",  # renamed to alc_eshop_api_discounts
        "keycloak",  # renamed to connector_keycloak
        "paginated_service_mixin",  # services are migrated to fastapi
        "alc_eshop_product_on_order",  # renamed to alc_eshop_api_products_on_order
        "alc_product_mto",  # replaced by product_route_mto
        "alc_eshop_veterinary_group",  # renamed to alc_eshop_api_veterinary_groups
        "alc_eshop_product_promotion_subscription",  # renamed to alc_eshop_api_promotion_subscriptions
        "alc_eshop_form",  # renamed to alc_eshop_api_forms
        "alc_eshop_services_orders",  # renamed to alc_eshop_api_orders
        "alc_eshop_services_orders_suite_channel",  # logic put into alc_eshop_api_orders
        "alc_eshop_services_deliveries",  # renamed to alc_eshop_api_deliveries
        "standard_service_mixin",  # no more used
        "alc_base_rest_api_doc",  # no more used
        "alc_eshop_partner_veterinary",  # renamed in alc_eshop_schema_address
        "alc_eshop_customer_sales_person",  # renamed in alc_eshop_api_customer
        "alc_eshop_sale_cart_info",  # moved into alc_eshop_api_cart
        "alc_eshop_sale_channel",  # replaced
        "alc_eshop_sale_suite_name",  # renamed alc_eshop_schema_sale_suite_name
        "alc_eshop_sale_qty_canceled",  # renamed alc_eshop_schema_sale_qty_canceled
        "alc_eshop_sale_no_backend",
        "alc_eshop_sale_product_unavailable",  # renamed alc_eshop_schema_sale_product_unavailable
        "alc_eshop_sale_no_cart_get",
        "alc_eshop_wishlist",
        "shopinvader_wishlist",  # replaced by shopinvader_api_wishlist
        "alc_eshop_filter_data",
        "shopinvader_product_stock",
        "shopinvader_product_stock_state",
        "alc_eshop_product_expiry",  # renamed alc_eshop_search_engine_product_expiry
        "alc_eshop_product_category_sequence",
        "alc_eshop_sale_cart_confirm",  # moved into alc_eshop_api_cart
        "alc_eshop_sale_cart_csv",  # moved into alc_eshop_api_cart
        "alc_eshop_sale_cart_suite_name",  # moved into alc_eshop_api_cart
        "alc_eshop_sale_cart_product_unavailable",  # renamed alc_eshop_api_cart_product_unavailable
        "alc_eshop_sale_cart_product_unavailable_pharmacy",  # renamed alc_eshop_schema_sale_product_unavailable_pharmacy
        "alc_shopinvader_fixes",
        "shopinvader_delivery_carrier",
        "shopinvader_sale_cart_delivery",
        "alc_eshop_api_delivery_carriers",  # renamed alc_eshop_cart_api_delivery
        "alc_eshop_sale_triple_discount",  # replaced by alc_eshop_schema_sale_triple_discount
        "shopinvader_auth_jwt",
        "alc_eshop_sale_cart_payment_info",  # renamed alc_eshop_schema_sale_payment
        "alc_eshop_sale_payment_info",  # replaced by alc_eshop_schema_sale_payment
        "connector_esb",  # renamed alc_connector_esb
        "alc_eshop_api_v2",
        "delivery_rounds",
        "delivery_rounds_alcyon",
        "specific_print",
        "specific_account",
        "specific_stock",
        "stock_picking_zone",
        "price_compute",
        "shopinvader_url_locales",  # replaced by alc_eshop_search_engine_product_url_locales
        "shopinvader_search_engine_update_vtgroups",  # replaced by alc_eshop_search_engine_update_veterinary_group
        "shopinvader_search_engine_update_specials",  # replaced by alc_eshop_search_engine_update_product_discount_special
        "alc_search_engine",
        "elasticsearch_product_cache",  # removed see #62795
        "alc_eshop_product_stock",  # replaced by alc_eshop_search_engine_product_stock
        "alc_shopinvader_category",  # replaced by alc_eshop_search_engine_category
        "shopinvader_assortment",  # replaced by shopinvader_search_engine_assortment
        "shopinvader_assortment_bind",  # replaced by alc_eshop_search_engine_assortment_bind
        "account_invoice_email",  # renamed to alc_account_invoice_email
    ]
    _logger.info("Modules to remove: %s", ",".join(modules_list))
    with cursor(DB_16_FINAL) as cr:
        query = """
            UPDATE ir_module_module
                SET state = 'to remove'
                WHERE name IN %s AND state NOT IN ('uninstallable', 'uninstalled')
        """
        openupgrade.logged_query(
            cr,
            query,
            (tuple(modules_list),),
        )


@task()
def set_modules_to_remove_core():
    """Set modules to remove in core as immediate uninstall does not work."""
    modules_list = [
        # quality_control and co_depends
        "mrp_subcontracting_quality",
        "quality_mrp_workorder_worksheet",
        "stock_barcode_quality_control_picking_batch",
        "stock_barcode_quality_control",
        "quality_control_picking_batch",
        "quality_control_worksheet",
        "quality_mrp_workorder",
        "quality_control_iot",
        "quality_mrp_workorder_iot",
        "purchase_mrp_workorder_quality",
        "quality_control",
        "quality_mrp",
        # mrp and co_depends"
        "mrp_subcontracting_quality",
        "mrp_account_enterprise",
        "mrp",
        "mrp_workorder_hr",
        "mrp_maintenance",
        "quality_mrp",
        "purchase_mrp_workorder_quality",
        "mrp_account",
        "mrp_product_expiry",
        "purchase_mrp",
        "quality_mrp_workorder_iot",
        "mrp_plm",
        "mrp_mps",
        "test_main_flows",
        "pos_mrp",
        "mrp_subcontracting_repair",
        "sale_mrp",
        "mrp_workorder_iot",
        "sale_mrp_margin",
        "mrp_subcontracting_enterprise",
        "mrp_workorder_plm",
        "mrp_subcontracting_account_enterprise",
        "mrp_subcontracting_account",
        "project_mrp",
        "mrp_subcontracting_dropshipping",
        "mrp_subcontracting",
        "quality_mrp_workorder",
        "stock_barcode_mrp_subcontracting",
        "mrp_workorder_hr_account",
        "mrp_repair",
        "mrp_subcontracting_studio",
        "mrp_workorder_expiry",
        "mrp_workorder",
        "quality_mrp_workorder_worksheet",
        "stock_barcode_mrp",
        "mrp_subcontracting_purchase",
        "mrp_subonctracting_landed_costs",
        "mrp_landed_costs",
        "spreadsheet_dashboard_mrp_account",
    ]
    _logger.info("Modules to remove: %s", ",".join(modules_list))
    with cursor(DB_16_FINAL) as cr:
        query = """
            UPDATE ir_module_module
                SET state = 'to remove'
                WHERE name IN %s AND state NOT IN ('uninstallable', 'uninstalled')
        """
        openupgrade.logged_query(
            cr,
            query,
            (tuple(modules_list),),
        )


@task()
def click_odoo_update_final():
    check_call(
        ["click-odoo-update", "-d", DB_16_FINAL, "--i18n-overwrite", "--update-all"]
    )


@task()
def deactivate_all_crons():
    # To avoid high charge at restart and undesired behaviors
    with cursor(DB_16_FINAL) as cr:
        query = """
            UPDATE ir_cron
                SET active = False
        """
        openupgrade.logged_query(
            cr,
            query,
        )
