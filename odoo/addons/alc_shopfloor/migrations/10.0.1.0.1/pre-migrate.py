# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_shopfloor.hooks import pre_init_hook


def migrate(cr, version):

    cr.execute(
        """
        select res_id from ir_model_data where name='picking_type_location_content_transfer'
    """
    )
    res = cr.fetchall()
    if res:
        # the picking type will be removed...
        cr.execute(
            """
        update stock_picking set picking_type_id=9 where picking_type_id=%s
        """,
            (res[0][0],),
        )

    pre_init_hook(cr)
