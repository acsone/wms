# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_special_delivery_round_as_manual(ctx):
    sql = """
    UPDATE procurement_group g
    SET carrier_id = (SELECT res_id
                      FROM ir_model_data
                      WHERE module = 'delivery_rounds'
                      AND name = 'delivery_carrier_manual_round_change')
    FROM stock_picking p, round_instance r
    WHERE (
      g.carrier_id IS NULL
      OR
      g.carrier_id = (SELECT res_id
                      FROM ir_model_data
                      WHERE module = '__setup__'
                      AND name = 'deliver_carrier_alcyon')
    )
    AND g.id = p.group_id
    AND r.id = p.delivery_round_id
    AND p.state not in ('done', 'cancel')
    AND r.template_id in (
      SELECT res_id FROM ir_model_data
      WHERE module = '__setup__'
      AND name IN ('delivery_template_comptoir', 'delivery_template_longterm')
    )
    """
    ctx.env.cr.execute(sql)


@anthem.log
def post(ctx):
    """POST 10.30.13"""
    set_special_delivery_round_as_manual(ctx)
