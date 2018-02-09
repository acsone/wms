# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def main(ctx):
    remove_stock_xml_export(ctx)


@anthem.log
def remove_stock_xml_export(ctx):
    """The xml export of stock level is not needed anymore"""
    try:
        rec = ctx.env.ref('connector_esb.esb_timestamp_stock')
    except ValueError:
        # Not here no need to delete it then
        pass
    else:
        if rec:
            rec.unlink()
