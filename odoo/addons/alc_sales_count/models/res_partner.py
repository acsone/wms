# © 2017 Julien Coux (Camptocamp)
# © 2018 Yannick Vaucher (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as PartnerBase


class ResPartner(PartnerBase):
    def _compute_sale_lines_count(self):
        for partner in self:
            domain = [
                ("state", "in", ["sale"]),
                ("order_id.partner_id", "=", partner.id),
                ("product_qty_remains_to_deliver", ">", 0),
            ]

            partner.sale_lines_count = len(self.env["sale.order.line"].search(domain))

    sale_lines_count = fields.Integer(compute="_compute_sale_lines_count")
