# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):

    openupgrade.update_module_moved_fields(
        cr,
        "delivery.carrier",
        ["use_specific_cost_calculation", "fixed_fee_for_delivery"],
        "specific_shipping_costs",
        "alc_shipping_fee",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "stock.picking.type",
        ["avoid_shipping_cost"],
        "specific_shipping_costs",
        "alc_shipping_fee",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order",
        ["used_for_delivery_fee", "used_for_fixed_fee", "fixed_extra_fee_for_delivery"],
        "specific_shipping_costs",
        "alc_shipping_fee",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "res.partner",
        ["help_with_fee", "help_with_fixed_fee"],
        "specific_sale",
        "alc_shipping_fee",
    )
