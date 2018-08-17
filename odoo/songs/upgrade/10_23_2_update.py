# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def change_saleorder_report(ctx):
    """Remove the toggle print menu in the center of the view sale order.

    Instead of changing the internal of the report generation and saving in
    ir.attachment, the button is not displayed. There is always the print
    button available in the action/state toolbar.

    """
    report = ctx.env.ref('sale.report_sale_order')
    report.unlink_action()


@anthem.log
def post(ctx):
    """ POST 10.23.2 """
    change_saleorder_report(ctx)
