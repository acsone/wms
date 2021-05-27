# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    names = (
        "stock_picking_type_rangement_medoc",
        "stock_picking_type_reassort_medoc",
        "stock_picking_type_medoc",
    )

    cr.execute(
        """
        UPDATE
            ir_model_data
        SET
            module = 'alc_shopfloor',
            noupdate = True
        WHERE
            module = '__setup__'
            AND name in %s
    """,
        (names,),
    )
