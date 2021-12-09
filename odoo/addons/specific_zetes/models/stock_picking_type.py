# -*- coding: utf-8 -*-
# © 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, tools

from .. import constants


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    zetes_picking_type = fields.Selection(
        [
            (constants.PICKING_ASSIGNMENT, "Customer"),
            (constants.RANGEMENT_ASSIGNMENT, "Rangement"),
            (constants.REASSORT_ASSIGNMENT, "Reassort"),
        ],
        string="Picking type",
    )

    passport = fields.Boolean("Enable passports")

    def toggle_passport(self):
        for rec in self:
            rec.passport = not rec.passport

    @api.model
    @tools.ormcache()
    def _get_id_by_zone_code(self):
        res = {}
        for rec in self.search([]):
            if rec.picking_zone_id.code:
                res[rec.picking_zone_id.code] = rec.id
        return res

    @api.model
    def _get_by_zone_code(self, code):
        _id = self._get_id_by_zone_code().get(code)
        if not _id:
            return self.browse()
        return self.browse(_id)

    @api.model
    def create(self, vals):
        result = super(StockPickingType, self).create(vals)
        self._get_id_by_zone_code.clear_cache(self)
        return result

    @api.multi
    def write(self, vals):
        result = super(StockPickingType, self).write(vals)
        self._get_id_by_zone_code.clear_cache(self)
        return result

    @api.multi
    def unlink(self):
        result = super(StockPickingType, self).unlink()
        self._get_id_by_zone_code.clear_cache(self)
        return result
