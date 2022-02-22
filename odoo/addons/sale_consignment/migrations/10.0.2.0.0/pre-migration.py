# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    # Move fields to specific_sale
    openupgrade.update_module_moved_fields(
        cr, "sale.order.line", ["is_consignment"], "specific_sale", "sale_consignment",
    )
