import importlib
import functools
import logging
import os

from click_odoo.env import OdooEnvironment
from odoo.addons.base_geoengine.geo_db import init_postgis
from odoo.modules import module
from openupgradelib import openupgrade
from setuptools_odoo import base_addons
from . import migrations
from .call import check_call
from .dbtools import copydb, psql_file, cursor, ref_id, recover_columns
from .pseudo_env import pseudo_env
from .venv import mkvenv

DB_10_SRC_NOT_CLEANED = "odoo-alcyon-prod"  # the db with geo fields..
DB_16_MIG = "alcyon-migrated"
DB_16_POSTMIG = "alcyon-16-postmig"
DB_16_RECETTE = "alcyon-16-recette"

tasks = []

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

# import all modules from the migrations package
for name in os.listdir(migrations.__path__[0]):
    if name.endswith(".py"):
        # we dynamically import the module
        # as from .migrations import name[:-3]
        # but without the dot
        importlib.import_module("tasks.migrations." + name[:-3])
        # __import__("tasks.migrations." + name[:-3], fromlist=["*"])


# get version from alc_all addons
def get_version():
    manifest = module.get_manifest("alc_all")
    return manifest["version"]


VERSION = get_version()


def task(f):
    """Decorator that register the tasks list."""
    tasks.append((f.__name__, f))
    return f


def _register_migration_scripts_in_tasks(prefix):
    """Register migrate method from modules into the migrations module.

    where modules are found by the fsmatch_pattern.

    :param prefix: The prefix of the modules to register.
    """
    for mod in dir(migrations):
        if mod.startswith(prefix):
            method = getattr(migrations, mod).migrate
            # The second argument is the method to call.
            # is the version but when a task is called, the version is not
            # passed as argument.
            # We create a closure to pass a default version as argument.

            def wrapped(mod=mod, method=method):
                # define attributes into the locals context
                # required by the openupgrade.migrate method
                pkg = importlib.machinery.ModuleSpec(
                    "tasks.migrations." + mod, None, is_package=True
                )
                locals().update(
                    {
                        "stage": mod.split("_")[1],
                        "pkg": pkg,
                        "pyfile": pkg.name + ".py",
                    }
                )
                with OdooEnvironment(DB_16_POSTMIG) as env:
                    method(env.cr, version=VERSION)

            tasks.append((mod, functools.partial(wrapped, mod=mod, method=method)))


@task
def copydb_16_postmig():
    copydb(DB_16_MIG, DB_16_POSTMIG)


@task
def ensure_postgis():
    with cursor(DB_16_POSTMIG) as cr:
        init_postgis(cr)


@task
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


@task
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


@task
def cleanup_stock_quant_package():
    psql_file(
        DB_16_POSTMIG,
        "psql/cleanup-stock-quant-package-product-packaging-id-fkey.sql",
    )


@task
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


@task
def migrate_account_payment_partner():
    # TODO verify number of move_line with a payment_mode_id
    with cursor(DB_16_POSTMIG) as cr:
        query = """
            UPDATE account_payment_mode
            SET show_bank_account_from_journal = true
            WHERE bank_account_link = 'fixed'
        """
        openupgrade.logged_query(cr, query)
        query = "ALTER TABLE account_move ADD payment_mode_id int4"
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


@task
def cleanup_queue_job():
    psql_file(DB_16_POSTMIG, "psql/cleanup-queue-job.sql")


@task
def migrate_product_packaging_level():
    with pseudo_env(DB_16_POSTMIG) as env:
        # Former version of the module is present
        tables = [("product_packaging_type", "product_packaging_level")]
        openupgrade.rename_tables(env.cr, tables)
        models = [("product.packaging.type", "product.packaging.level")]
        openupgrade.rename_models(env.cr, models)
        fields = [
            (
                "product.packaging",
                "product_packaging",
                "packaging_level_id",
                "packaging_level_id",
            )
        ]
        openupgrade.rename_fields(env, fields, no_deep=True)

        modules = [("product_packaging_type", "product_packaging_level")]
        openupgrade.update_module_names(env.cr, modules, merge_modules=True)
        openupgrade.rename_xmlids(
            env.cr,
            [
                (
                    "product_packaging_level.product_packaging_type_default",
                    "product_packaging_level.product_packaging_level_default",
                )
            ],
        )


@task
def cleanup_partner_discount_rel():
    psql_file(DB_16_POSTMIG, "psql/cleanup-partner-discount-rel.sql")


@task
def fix_product_packaging_data_and_structure():
    recover_columns(DB_10_SRC_NOT_CLEANED, DB_16_POSTMIG, "product_packaging")


@task
def recover_partner_geopoint():
    recover_columns(
        DB_10_SRC_NOT_CLEANED,
        DB_16_POSTMIG,
        "res_partner",
        {"geo_point": "geometry(Point, 3857)"},
    )


@task
def recover_round_template_geo_polygon_shape():
    recover_columns(
        DB_10_SRC_NOT_CLEANED,
        DB_16_POSTMIG,
        "round_template",
        {"geo_polygon_shape": "geometry(MultiPolygon,3857)"},
    )


@task
def delare_alc_product_category_data_module_as_installed():
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
            SELECT 'alc_product_category_data', 'to upgrade', author, website, license, shortdesc, description, auto_install, '16.0.1.0.0', sequence, category_id, icon, create_uid, create_date, write_uid, write_date
            FROM ir_module_module
            WHERE name = 'specific_data'
            """
        openupgrade.logged_query(cr, query)


@task
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


_register_migration_scripts_in_tasks("pre_")


@task
def click_odoo_update():
    check_call(["venv-16/bin/click-odoo-update", "-d", DB_16_POSTMIG])


_register_migration_scripts_in_tasks("post_")
