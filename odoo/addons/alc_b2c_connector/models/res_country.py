# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, models, tools
from odoo.exceptions import ValidationError


class ResCountry(models.Model):
    _inherit = "res.country"

    @api.model
    @tools.ormcache()
    def _get_id_by_code(self):
        return {c.code: c.id for c in self.sudo().search([])}

    @api.model
    @tools.ormcache()
    def _get_codes(self):
        codes = self._get_id_by_code().keys()
        codes.sort()
        return codes

    @api.model
    def _get_by_code(self, code):
        _id = self._get_id_by_code().get(code)
        if not _id:
            raise ValidationError(_("Unknown country code %s") % code)
        return self.browse(_id)

    @api.model
    def create(self, vals):
        result = super(ResCountry, self).create(vals)
        self._get_id_by_code.clear_cache(self)
        self._get_codes.clear_cache(self)
        return result

    @api.multi
    def write(self, vals):
        result = super(ResCountry, self).write(vals)
        self._get_id_by_code.clear_cache(self)
        self._get_codes.clear_cache(self)
        return result

    @api.multi
    def unlink(self):
        result = super(ResCountry, self).unlink()
        self._get_id_by_code.clear_cache(self)
        self._get_codes.clear_cache(self)
        return result
