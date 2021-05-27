# -*- coding: utf-8 -*-
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    # If the DB does not contain Alcyon stock setup structure, create it
    location = "stock_location_medoc"
    cr.execute(
        "SELECT model, name, res_id FROM ir_model_data WHERE module = '__setup__' and name = %s",
        (location,),
    )
    res = cr.fetchone()
    if not res:
        cr.execute(
            """
            INSERT INTO ir_model_data (create_uid, write_date, date_update, noupdate, model, name, module, res_id)
            SELECT 1, current_timestamp, current_timestamp, true, model, %s, '__setup__', res_id
            FROM ir_model_data WHERE module = 'stock' and name = 'stock_location_stock'
        """,
            (location,),
        )

    cr.execute(
        """
        SELECT location_id FROM stock_location WHERE id in (
            SELECT res_id FROM ir_model_data WHERE module = 'stock' and name = 'stock_location_stock'
        )
        """
    )
    VLB_location_id = cr.fetchone()[0]

    location = "stock_location_reserve_medoc"
    cr.execute(
        "SELECT model, name, res_id FROM ir_model_data WHERE module = '__setup__' and name = %s",
        (location,),
    )
    res = cr.fetchone()
    if not res:
        cr.execute(
            """
            INSERT INTO ir_model_data (create_uid, write_date, date_update, noupdate, model, name, module, res_id)
            VALUES (1, current_timestamp, current_timestamp, true, 'stock.location', %(name)s, '__setup__', %(res_id)s)
            """,
            {"name": location, "res_id": VLB_location_id},
        )
