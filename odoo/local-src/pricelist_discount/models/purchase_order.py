# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    supplier_promotion_allowed = fields.Boolean(
        string='Supplier promotion allowed',
        related='partner_id.supplier_promotion_purchase_allowed',
        readonly=True
    )
