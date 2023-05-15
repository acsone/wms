# Copyright 2018 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, fields
from odoo.exceptions import UserError

from odoo.addons.delivery.models.delivery_carrier import (
    DeliveryCarrier as DeliveryCarrierBase,
)


class DeliveryCarrier(DeliveryCarrierBase):

    use_specific_cost_calculation = fields.Boolean(string="Alcyon specific cost")
    fixed_fee_for_delivery = fields.Float(string="Fixed extra fee")

    def unlink(self):
        if self.env["res.partner"].search(
            [("property_delivery_carrier_id", "in", self.ids)]
        ):
            raise UserError(_("You cannot delete a record linked from a partner"))
        return super().unlink()
