# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # Moved fields from alc_b2c_connector
    openupgrade.update_module_moved_fields(
        cr, "res.partner", ["is_b2c_customer"], "alc_b2c_connector", "alc_b2c_partner"
    )

    # Moved xml_id from alc_b2c_connector
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "alc_b2c_connector.res_partner_category_b2c_customer",
                "alc_b2c_partner.res_partner_category_b2c_customer",
            )
        ],
    )
