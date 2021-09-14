# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    cr.execute(
        """
        UPDATE
            res_partner
        SET
            not_in_dynamic_delivery_round = true
        WHERE
            is_b2c_customer = true
        """
    )
