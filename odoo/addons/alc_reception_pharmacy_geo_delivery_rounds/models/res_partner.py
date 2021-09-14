# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends(lambda self: self._is_delivered_by_alcyon_depends())
    @api.multi
    def _compute_is_delivered_by_alcyon(self):
        res = super(ResPartner, self)._compute_is_delivered_by_alcyon()
        for rec in self:
            if rec.not_in_dynamic_delivery_round:
                continue
            rec.is_delivered_by_alcyon = (
                len(rec.partner_shipping_id.round_template_ids) > 0
            )
        return res

    @api.model
    def _is_delivered_by_alcyon_depends(self):
        res = super(ResPartner, self)._is_delivered_by_alcyon_depends()
        res.extend(
            [
                "partner_shipping_id.round_template_ids",
                "partner_shipping_id.not_in_dynamic_delivery_round",
            ]
        )
        return res
