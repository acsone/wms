# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from odoo import _, api
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_country import Country

_logger = logging.getLogger(__name__)


class ResCountry(Country):
    @api.model
    def _get_by_code(self, code):
        country = self.search([("code", "=", code)], limit=1)
        if not country:
            _logger.error("Unknown country code %s", code)
            msg = _("Unknown country code {code}").format(code=code)
            raise ValidationError(msg)
        return country
