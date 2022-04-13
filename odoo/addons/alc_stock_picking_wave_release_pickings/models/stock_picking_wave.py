# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPickingWave(models.Model):

    _inherit = "stock.picking.wave"

    state = fields.Selection(selection_add=[("released", "Released")])
    release_not_allowed = fields.Boolean(
        default=False, compute="_compute_release_not_allowed"
    )

    @api.depends(
        "picking_ids",
        "picking_ids.pack_operation_ids",
        "picking_ids.pack_operation_ids.qty_done",
    )
    def _compute_release_not_allowed(self):
        for rec in self:
            rec.release_not_allowed = rec.state in (
                "done",
                "cancel",
                "released",
            ) or any(rec.mapped("picking_ids.pack_operation_ids.qty_done"))

    def release(self):
        if any([rec.release_not_allowed for rec in self]):
            raise ValidationError(_("You cannot release a wave with started pickings"))
        # 2 steps to propagate info from wave to pickings because we first need
        # to propagate printed and operator_id, then unlink the pickings.
        # If we do everything in one line, pickings are unlinked before printed
        # is set to False, then it never propagates.
        self.write({"state": "released", "printed": False, "operator_id": False})
        return self.write({"picking_ids": [(5, None, None)]})

    def unlink(self):
        config_param = self.env["ir.config_parameter"]
        constrain_unlink = int(
            config_param.get_param("constrain_release_picking_wave_before_unlink", 0)
        )
        if constrain_unlink and any(
            [rec.state not in ("cancel", "released") for rec in self]
        ):
            raise ValidationError(
                _("You cannot delete waves that are not canceled or released")
            )
        return super(StockPickingWave, self).unlink()
