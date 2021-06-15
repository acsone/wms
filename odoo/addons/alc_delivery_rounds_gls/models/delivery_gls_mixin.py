# -*- coding: utf-8 -*-
# Copyright 2021 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DeliveryGlsMixin(models.AbstractModel):
    """Forbids automatic delivery if some GLS packages were not sent yet.
       This is because each GLS package needs to be manually printed.
    """

    _name = "delivery.gls.mixin"

    is_gls_sent = fields.Boolean(
        "Are all GLS pickings sent to GLS.", compute="_compute_is_gls_sent",
    )

    def _raise_if_not_sent(self):
        """Raise a validation error if is_gls_sent is False."""
        if self.filtered(lambda ri: not ri.is_gls_sent):
            msg = _("You need to confirm manually all GLS packages")
            raise ValidationError(msg)

    @api.depends("picking_ids.state", "picking_ids.delivery_type")
    def _compute_is_gls_sent(self):
        """It is not sent yet if some GLS picking has not been confirmed yet."""
        filter_picking = lambda p: p.delivery_type == "gls" and p.state != "done"
        for ri in self:
            ri.is_gls_sent = not ri.picking_ids.filtered(filter_picking)
