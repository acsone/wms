# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_partner_delivered_by_alcyon.models.res_partner import (
    ResPartner as Partner,
)


class ResPartner(Partner):

    partner_shipping_id = fields.Many2one[Partner](
        string="Delivery Address",
        compute="_compute_partner_shipping_id",
    )

    @api.depends("child_ids")
    def _compute_partner_shipping_id(self):
        """Trigger the change of the shipping address if the customer is modified."""
        for rec in self:
            address = rec.address_get(["delivery", "invoice"])
            rec.partner_shipping_id = address["delivery"]
