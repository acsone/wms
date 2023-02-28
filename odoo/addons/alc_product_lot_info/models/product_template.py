# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models import product_template


class ProductTemplate(product_template.ProductTemplate):

    lot_ids = fields.One2many("stock.lot", string="Lots", compute="_compute_lot_ids")

    def _compute_lot_ids(self):
        now = fields.Datetime.now()
        for rec in self:
            lot_ids = rec.mapped("product_variant_ids.lot_ids").filtered(
                lambda l: not l.removal_date or l.removal_date > now
            )
            rec.lot_ids = lot_ids.sorted(
                key=lambda l: (l.qty_available, l.expiration_date), reverse=True
            )
