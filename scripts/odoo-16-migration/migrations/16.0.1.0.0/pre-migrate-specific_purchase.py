# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _move_product_template(env):
    _logger.info("product.template: move field 'supplier_id'")
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        ["supplier_id"],
        "specific_purchase",
        "alc_product_supplier",
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


@openupgrade.migrate()
def migrate(env, version):
    _move_product_template(env)
    _mig_alc_purchase_order_discount(env)
