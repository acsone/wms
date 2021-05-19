# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):

    _inherit = "stock.picking"

    @api.constrains("operator_id", "delivery_round_id")
    def _check_allowed_operator(self):
        """ Check operator is allowed

        If a delivery round is linked to the picking and a list of
        allowed operators is defined on the delivery round, the operator
        must be into this list.

        The constrains doesn't depend on the delivery_round_id.operator_ids
        fields since we must avoid that the constrains is rechecked each
        time the list change on the delivery round.
        """
        for rec in self:
            if rec.state in ("donce", "cancel"):
                continue
            if not rec.delivery_round_id.operator_ids:
                continue
            if not rec.operator_id:
                continue
            if not rec.delivery_round_id:
                continue
            if rec.operator_id not in rec.delivery_round_id.operator_ids:
                raise ValidationError(
                    _(
                        u"Operator {operator_name} is not into the list of allowed "
                        u"operators for the delivery round {round_name} "
                        u"({allowed_operator_names})."
                    ).format(
                        operator_name=rec.operator_id.name,
                        round_name=rec.delivery_round_id.display_name,
                        allowed_operator_names=u" ,".join(
                            rec.delivery_round_id.mapped("operator_ids.display_name")
                        ),
                    )
                )
