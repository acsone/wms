# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    # Move fields to alc_sale_invoicing_policy
    openupgrade.update_module_moved_fields(
        cr,
        "sale.order.line",
        ["product_qty_unavailable"],
        "specific_sale",
        "procurement_sale",
    )
