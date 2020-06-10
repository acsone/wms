# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _get_so_to_invoice(self):
        # a complete override of alc_sale_invoicing_on_transfer since it's not
        # possivle to use specific operators into odoo's domain and
        # we don't want to strore data from the partner nor from the payment
        # mode on so to avoid trouble id values changes on the partner and
        # the payment mode (recompute launched on a large amount of records
        SaleOrder = self.env["sale.order"]
        picking_types = self.env["stock.picking.type"].search(
            [("create_invoice_on_transfer", "=", True)]
        )
        create_invoice_pickings = self.filtered(
            lambda picking: picking.picking_type_id in picking_types
        )
        if False:  # not create_invoice_pickings:
            return SaleOrder
        proc_groups = create_invoice_pickings.mapped("move_lines.group_id")
        if not proc_groups:
            return SaleOrder
        query = """
        SELECT
            so.id
        FROM
            sale_order AS so
            INNER JOIN res_partner AS partner
                ON partner.id = so.partner_invoice_id
            LEFT JOIN account_payment_mode AS pm
                ON pm.id = so.payment_mode_id
        WHERE
            so.invoice_status = 'to invoice'
            AND so.procurement_group_id in %s
            AND COALESCE(pm.invoice_grouping, partner.invoice_grouping) = 'by_delivery'
        """
        cr = self.env.cr
        cr.execute(query, (tuple(proc_groups.ids),))
        so_ids = [r[0] for r in cr.fetchall()]
        return SaleOrder.browse(so_ids)
