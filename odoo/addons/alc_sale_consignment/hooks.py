# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    # Moved xml_id from sale_consignment
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "sale_consignment.stock_location_consignment",
                "alc_sale_consignment.stock_location_consignment",
            )
        ],
    )
    openupgrade.update_module_moved_fields(
        cr,
        "res.partner",
        ["property_stock_consignment_customer"],
        "sale_consignment",
        "alc_sale_consignment",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order",
        ["is_consignment"],
        "sale_consignment",
        "alc_sale_consignment",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order.line",
        ["is_consignment"],
        "sale_consignment",
        "alc_sale_consignment",
    )
