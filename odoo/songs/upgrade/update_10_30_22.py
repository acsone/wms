# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from itertools import groupby
import anthem

MIGR_LBL = '[MIGRATION]'


def is_migration(invoice):
    return MIGR_LBL in invoice.name


def write_invoiced_qty1(ctx, pol_ids):
    updated_po = None
    product_list = []
    for pol in ctx.env['purchase.order.line'].browse(pol_ids):
        invoice = pol.invoice_lines.mapped('invoice_id')
        # check we have a simple case of a single migration
        # invoice
        if len(invoice) == 1 and is_migration(invoice):
            inv_l = pol.invoice_lines
            if len(inv_l) != 1:
                # XXX not implemented
                continue
            inv_l.write({
                'quantity': pol.qty_received,
                'price_unit': 0.0,
            })
        elif not invoice:
            invoice = pol.order_id.invoice_ids
            if len(invoice) != 1 or not is_migration(invoice):
                # XXX not implemented
                continue
            inv_l_data = invoice._prepare_invoice_line_from_po_line(pol)
            inv_l_data.update({
                'invoice_id': invoice.id,
                'price_unit': 0.0,
            })
            inv_l = ctx.env['account.invoice.line'].create(inv_l_data)
            inv_l._set_additional_fields(invoice)
        else:
            # XXX not implemented
            continue
        pol.write({
            'qty_invoiced': pol.qty_received,
            'qty_to_invoice': 0,
        })
        product_list.append(pol.product_id.name)
        if not updated_po:
            updated_po = pol.order_id
    if updated_po:
        products = ','.join(product_list)
        msg = "Invoiced quantities updated for %s" % products
        updated_po.message_post(body=msg)


def write_invoiced_qty2(ctx, pol_data):
    """ For lines that have been edited, compare values
    with db2 local copy.

    Thus we set as invoice only what was set as received
    the day of go live.

    Having multiple existing invoices is not implemented.
    """
    updated_po = None
    product_list = []
    for pol_id, dcfqul in pol_data.iteritems():
        pol = ctx.env['purchase.order.line'].browse(pol_id)
        invoice = pol.invoice_lines.mapped('invoice_id')
        # check we have a simple case of a single migration
        # invoice
        if len(invoice) == 1 and is_migration(invoice):
            if pol.qty_invoiced == dcfqul:
                # quit early, some additional qty have been
                # received and invoicing is right
                continue
            inv_l = pol.invoice_lines
            if len(inv_l) != 1:
                # XXX not implemented
                continue
            if inv_l.quantity != 0:
                # XXX not implemented
                continue
            inv_l.quantity = dcfqul
        elif not invoice:
            invoice = pol.order_id.invoice_ids
            if len(invoice) != 1 or not is_migration(invoice):
                # XXX not implemented
                continue
            inv_l_data = invoice._prepare_invoice_line_from_po_line(pol)
            inv_l_data['invoice_id'] = invoice.id
            inv_l_data['quantity'] = dcfqul
            ctx.env['account.invoice.line'].create(inv_l_data)
        else:
            # XXX not implemented
            continue
        pol.write({
            'qty_invoiced': dcfqul,
            'qty_to_invoice': pol.qty_received - dcfqul
        })
        product_list.append(pol.product_id.name)
        if not updated_po:
            updated_po = pol.order_id
    if updated_po:
        products = ','.join(product_list)
        msg = "Invoiced quantities updated for %s" % products
        updated_po.message_post(body=msg)


def fix_purchase(ctx, purchases, modified=False):
    for p, purchase_lines in purchases:
        if not modified:
            pol_ids = [pol[1] for pol in purchase_lines]
            num_pol = len(pol_ids)
        else:
            pol_data = dict((pol[1], pol[2]) for pol in purchase_lines)
            num_pol = len(pol_data)
        with ctx.log("PO %s : %s lines" % (p, num_pol)):
            if not modified:
                write_invoiced_qty1(ctx, pol_ids)
            else:
                write_invoiced_qty2(ctx, pol_data)


@anthem.log
def fix_invoiced_qty_on_imported_purchase_order1(ctx):
    """ For all imported purchase in open state
    with mismatching received and invoiceds quantities

    Update the [MIGRATION] invoice with the received quantities.

    Here we take care of the easiest cases where nothing happened
    on those purchase order line since it was imported.
    """
    query = """
SELECT po.id, pol.id FROM purchase_order_line pol
  INNER JOIN purchase_order po ON po.id = pol.order_id
  LEFT JOIN stock_move as m ON m.purchase_line_id = pol.id
  WHERE po.name !~ '^PO'
   AND po.state != 'done'
   AND m.id IS NOT NULL
   AND pol.write_date <= '2018-12-04'
   AND pol.qty_received > pol.qty_invoiced
  ORDER BY po.id
    """
    ctx.env.cr.execute(query)
    rows = ctx.env.cr.fetchall()
    if not len(rows):
        return
    # group by purchase
    purchases = groupby(rows, lambda r: r[0])
    with ctx.log("Fixing %s purchases" % len(rows)):
        fix_purchase(ctx, purchases)


@anthem.log
def fix_invoiced_qty_on_imported_purchase_order2(ctx):
    """ For all imported purchase in open state
    with mismatching received and invoiceds quantities

    Update the [MIGRATION] invoice with the received quantities.

    Here we take care of the hardest part. Which is purchase order
    lines that got updated since it was imported.

    This requires careful checks and steps.
    """
    query = """
SELECT po.id, pol.id, det.dcfqul FROM purchase_order_line pol
  INNER JOIN purchase_order po ON po.id = pol.order_id
  LEFT JOIN stock_move as m ON m.purchase_line_id = pol.id
  INNER JOIN db2_pdetcdfo det ON det.dcfsui::text = po.name
    AND det.dcfnli = pol.sequence
  WHERE po.name !~ '^PO'
   AND po.state != 'done'
   AND m.id IS NOT NULL
   AND pol.write_date > '2018-12-04'
   AND pol.qty_received > pol.qty_invoiced
   AND det.dcfqul > 0
  GROUP BY po.id, pol.id, det.dcfqul
  ORDER BY po.id
    """
    ctx.env.cr.execute(query)
    rows = ctx.env.cr.fetchall()
    if not len(rows):
        return
    # group by purchase
    purchases = groupby(rows, lambda r: r[0])
    with ctx.log("Fixing %s purchases that had changes" % len(rows)):
        fix_purchase(ctx, purchases, modified=True)


@anthem.log
def post_full(ctx):
    fix_invoiced_qty_on_imported_purchase_order1(ctx)
    fix_invoiced_qty_on_imported_purchase_order2(ctx)
