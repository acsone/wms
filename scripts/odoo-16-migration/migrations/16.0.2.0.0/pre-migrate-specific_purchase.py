# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _mig_alc_product_supplier(env):
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        ["supplier_id", "supplier_rel_id", "vendor_product_code"],
        "specific_purchase",
        "alc_product_supplier",
    )


def _mig_alc_product_nb_days_out_of_stock(env):
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        ["nb_days_out_of_stock"],
        "specific_purchase",
        "alc_product_nb_days_out_of_stock",
    )


def _mig_alc_purchase_order_discount(env):
    env.cr.execute(
        """
        UPDATE purchase_order_line set price_unit=price_unit_base;
        ALTER TABLE purchase_order_line ADD COLUMN IF NOT EXISTS discount NUMERIC;
        UPDATE purchase_order_line
        SET discount=100-((100-discount_global) * (100-promotion_supplier)/100);
        """
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.supplierinfo",
        ["discount_purchase"],
        "pricelist_discount",
        "alc_purchase_order_discount",
    )
    field_spec = [
        (
            "product.supplierinfo",
            "product._supplierinfo",
            "discount_purchase",
            "discount",
        )
    ]
    openupgrade.rename_fields(env=env, field_spec=field_spec, no_deep=True)

    openupgrade.update_module_moved_fields(
        env.cr,
        "purchase.order.line",
        ["discount_global", "promotion_supplier"],
        "specific_purchase",
        "alc_purchase_order_discount",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "res.partner",
        ["supplier_discount"],
        "specific_purchase",
        "alc_purchase_order_discount",
    )


def _mig_alc_purchase_order_date_planned(env):
    openupgrade.update_module_moved_fields(
        env.cr,
        "res.partner",
        ["delivery_lead_time"],
        "specific_purchase",
        "alc_purchase_order_date_planned",
    )


def _mig_alc_stock_scheduler_filter(env):
    # no need for transient model migration procurement_orderpoint_compute replaced by
    # stock_scheduler_compute
    openupgrade.update_module_moved_fields(
        env.cr,
        "res.partner",
        [
            "is_manage_day_1",
            "is_manage_day_2",
            "is_manage_day_3",
            "is_manage_day_4",
            "is_manage_day_5",
            "is_manage_day_6",
            "is_manage_day_7",
        ],
        "specific_purchase",
        "alc_stock_scheduler_filter",
    )


def _mig_bank_holiday(env):
    # FIXME: is this table used any more, the data in the db are for 2017 and 2018
    pass


def _mig_acl_product_supplierinfo_import(env):
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.supplierinfo",
        ["product_cnk_code"],
        "specific_purchase",
        "acl_product_supplierinfo_import",
    )


def _mig_purchase_order_user(env):
    if not openupgrade.column_exists(env.cr, "purchase_order", "responsible_id"):
        return
    env.cr.execute(
        """
        ALTER TABLE purchase_order ADD COLUMN IF NOT EXISTS user_id integer;
        UPDATE purchase_order
        SET user_id=responsible_id;
        """
    )


def _mig_alc_purchase_order_bo_line(env):
    openupgrade.update_module_moved_fields(
        env.cr,
        "purchase.order",
        ["nbr_lines", "nbr_lines_bo"],
        "specific_purchase",
        "alc_purchase_order_bo_line",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "purchase.order.line",
        ["is_bo_line"],
        "specific_purchase",
        "alc_purchase_order_bo_line",
    )


def _mig_alc_purchase_order_total_weight(env):
    openupgrade.update_module_moved_fields(
        env.cr,
        "purchase.order",
        ["total_weight"],
        "specific_purchase",
        "alc_purchase_order_total_weight",
    )


@openupgrade.migrate()
def migrate(env, version):
    _mig_alc_product_supplier(env)
    _mig_alc_product_nb_days_out_of_stock(env)
    _mig_alc_purchase_order_discount(env)
    _mig_alc_purchase_order_date_planned(env)
    _mig_alc_stock_scheduler_filter(env)
    _mig_bank_holiday(env)
    _mig_acl_product_supplierinfo_import(env)
    _mig_purchase_order_user(env)
    _mig_alc_purchase_order_bo_line(env)
    _mig_alc_purchase_order_total_weight(env)
