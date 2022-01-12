# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """

    # Rename xml_id for sav_location
    openupgrade.rename_xmlids(
        cr, [("__export__.stock_location_14416", "alc_mrp_repair.sav_stock_location",)],
    )
