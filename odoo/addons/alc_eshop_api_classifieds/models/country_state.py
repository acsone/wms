# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.tools.cache import ormcache

from odoo.addons.base.models import res_country


class CountryState(res_country.CountryState):
    @api.model
    @ormcache()
    def _get_belgium_state_id_by_code(self):
        """Return a mapping of state code to state id for states in Belgium."""
        domain = [("country_id", "=", self.env.ref("base.be").id)]
        state = self.env["res.country.state"].sudo().search(domain)
        return {s.code: s.id for s in state}

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self._get_belgium_state_id_by_code.clear_cache(self)
        return res

    def write(self, vals):
        res = super().write(vals)
        self._get_belgium_state_id_by_code.clear_cache(self)
        return res

    def unlink(self):
        res = super().unlink()
        self._get_belgium_state_id_by_code.clear_cache(self)
        return res
