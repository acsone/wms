# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_analytic_account_purchase_order_line(ctx):
    """ update translation """
    po_lines = ctx.env['purchase.order.line'].search([('order_id.name',
                                                       'not like',
                                                       'PO'),
                                                      ('order_id.state', '!=',
                                                       'done'),
                                                      ('account_analytic_id',
                                                       '=', None)
                                                      ]
                                                     )
    sql = """
    UPDATE purchase_order_line SET account_analytic_id = %s where id = %s;
    """
    for ctp, po_line in enumerate(po_lines, 1):
        ctx.log_line("Work on %s %s %s" % (ctp, len(po_lines),
                                           po_line.order_id.name))
        analytic_account_id = po_line.product_id.expense_analytic_account_id.id
        if not analytic_account_id:
            analytic_account_id =\
                po_line.product_id.categ_id.expense_analytic_account_id.id
        if analytic_account_id:
            ctx.log_line("UPDATE %s" % (po_line.id))
            ctx.env.cr.execute(sql, (analytic_account_id, po_line.id))
        else:
            ctx.log_line("Analytic account still missing" % (po_line.id))


@anthem.log
def post(ctx):
    set_analytic_account_purchase_order_line(ctx)
