# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models
from odoo.exceptions import UserError


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    use_specific_cost_calculation = fields.Boolean(string="Alcyon specific cost")

    def unlink(self):
        if self.env["res.partner"].search(
            [("property_delivery_carrier_id", "in", self.ids)]
        ):
            raise UserError(_("You cannot delete a record linked from a partner"))
        super(DeliveryCarrier, self).unlink()
