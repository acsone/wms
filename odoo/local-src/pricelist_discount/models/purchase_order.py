# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    supplier_promotion_allowed = fields.Boolean(
        string='Supplier promotion allowed',
        states={
            'purchase': [('readonly', True)],
            'done': [('readonly', True)],
            'cancel': [('readonly', True)],
        },
    )

    @api.onchange('partner_id')
    def onchange_partner_id_supplier_promotion_purchase_allowed(self):
        self.supplier_promotion_allowed = (
            self.partner_id.supplier_promotion_purchase_allowed
        )
