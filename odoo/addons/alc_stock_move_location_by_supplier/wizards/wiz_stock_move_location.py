# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.osv.expression import FALSE_DOMAIN

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.stock_move_location.wizard.stock_move_location import (
    StockMoveLocationWizard,
)


class WizStockMoveLocation(StockMoveLocationWizard):
    _inherit = "wiz.stock.move.location"

    supplier_ids = fields.Many2many[Partner](string="Suppliers")

    supplier_ids_domain = fields.Binary(compute="_compute_supplier_ids_domain")

    @api.depends("origin_location_id")
    def _compute_supplier_ids_domain(self):
        for wizard in self:
            quants = self.env["stock.quant"].search(
                wizard.with_context(skip_supplier_domain=True)._get_quants_domain()
            )
            suppliers = quants.mapped("product_id.supplier_id")
            if suppliers:
                wizard.supplier_ids_domain = [("id", "in", suppliers.ids)]
            else:
                wizard.supplier_ids_domain = FALSE_DOMAIN

    def _get_quants_domain(self):
        domain = super()._get_quants_domain()
        if not self.env.context.get("skip_supplier_domain") and self.supplier_ids:
            domain += [("product_id.supplier_id", "in", self.supplier_ids.ids)]
        return domain

    @api.onchange("supplier_ids")
    def onchange_supplier_ids(self):
        self._reset_stock_move_location_lines()
