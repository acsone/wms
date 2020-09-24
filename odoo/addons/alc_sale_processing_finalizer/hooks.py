# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    cr.execute(
        "SELECT model, name, res_id FROM ir_model_data WHERE module = '__setup__' and name = 'deliver_carrier_long_term'"
    )

    res = cr.fetchone()
    if not res:
        return

    cr.execute(
        """
        INSERT INTO ir_model_data (create_uid, write_date, date_update, noupdate, model, name, module, res_id) VALUES
        (1, current_timestamp, current_timestamp, true, %(model)s, %(name)s, 'alc_sale_processing_finalizer', %(res_id)s )

    """,
        {"model": res[0], "name": res[1], "res_id": res[2]},
    )

    cr.execute(
        "SELECT  model, name, res_id FROM ir_model_data WHERE module = '__export__' and name = 'mail_template_30'"
    )
    res = cr.fetchone()
    if not res:
        return

    cr.execute(
        """
        INSERT INTO ir_model_data (create_uid, write_date, date_update, noupdate, model, name, module, res_id) VALUES
        (1, current_timestamp, current_timestamp, true, %(model)s, %(name)s, 'alc_sale_processing_finalizer', %(res_id)s )

    """,
        {"model": res[0], "name": res[1], "res_id": res[2]},
    )
