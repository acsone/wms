# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.tools.cache import ormcache

from odoo.addons.sale_channel.models.sale_channel import SaleChannel as SaleChannelBase


class SaleChannel(SaleChannelBase):

    is_internal = fields.Boolean(string="Internal?")
    code = fields.Char()

    @api.model
    @ormcache()
    def _get_id_by_code(self):
        return {r.code: r.id for r in self.search([])}

    @api.model
    def _get_id_from_code(self, code):
        return self._get_id_by_code().get(code)

    @api.model
    @ormcache()
    def _get_internal_ids(self):
        return self.search([("is_internal", "=", True)]).ids

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        res._get_internal_ids.clear_cache(self)
        res._get_id_by_code.clear_cache(self)
        return res

    def write(self, vals):
        res = super().write(vals)
        if "is_internal" in vals:
            self._get_internal_ids.clear_cache(self)
        if "code" in vals:
            self._get_id_by_code.clear_cache(self)
        return res

    def unlink(self):
        res = super().unlink()
        self._get_internal_ids.clear_cache(self)
        res._get_id_by_code.clear_cache(self)
        return res
