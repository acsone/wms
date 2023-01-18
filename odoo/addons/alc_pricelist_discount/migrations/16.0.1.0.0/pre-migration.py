# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate(cr, version):
    # Move fields to specific_sale
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order",
        ["pricelist_discount", "discount_pricelist_ids"],
        "pricelist_discount",
        "alc_pricelist_discount",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order",
        ["discount_item_id"],
        "pricelist_discount",
        "alc_pricelist_discount",
    )
