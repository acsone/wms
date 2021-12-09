# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class PickingZone(models.Model):

    _inherit = "picking.zone"

    @api.model
    def create(self, vals):
        result = super(PickingZone, self).create(vals)
        self.env["stock.picking.type"]._get_id_by_zone_code.clear_cache(self)
        return result

    @api.multi
    def write(self, vals):
        result = super(PickingZone, self).write(vals)
        self.env["stock.picking.type"]._get_id_by_zone_code.clear_cache(self)
        return result

    @api.multi
    def unlink(self):
        result = super(PickingZone, self).unlink()
        self.env["stock.picking.type"]._get_id_by_zone_code.clear_cache(self)
        return result
