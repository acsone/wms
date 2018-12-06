
# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import add_xmlid


@anthem.log
def create_vat_tax_group(ctx):
    """A group has been added on prod so deal with it here."""
    xid = 'stock_delivery_note.vat_tax_group'
    vat_tax_group = ctx.env.ref(xid, raise_if_not_found=False)
    if vat_tax_group:
        return
    group = ctx.env['account.tax.group'].search(
        [('name', '=', 'TVA')],
        limit=1,
    )
    if not len(group):
        # Create a tax group for vat
        group = ctx.env['account.tax.group'].create({
            'name': 'TVA',
            'sequence': 10,
        })
    add_xmlid(ctx, group, xid)
