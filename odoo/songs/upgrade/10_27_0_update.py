# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import add_xmlid


XID_PRODUCT_TMPL = '__import__.product_{}_product_template'


@anthem.log
def fix_product_template_xids(ctx):
    """ Fix missing xmlids on few products """
    query = (
        "SELECT id, default_code"
        " FROM product_template"
        " WHERE id NOT IN"
        " (SELECT res_id FROM ir_model_data WHERE model = 'product.template')"
    )
    ctx.env.cr.execute(query)
    rows = ctx.env.cr.fetchall()
    for rec_id, default_code in rows:
        if default_code == 'DIVERS':
            continue
        rec = ctx.env['product.template'].browse(rec_id)
        xid = XID_PRODUCT_TMPL.format(default_code)
        add_xmlid(ctx, rec, xid)
