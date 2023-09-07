# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import fields

from odoo.addons.account_intrastat.models.res_country import ResCountry as Country


class ResCountry(Country):
    """Will be overriden by corresponding alce module."""

    is_intrastat = fields.Boolean(related="intrastat")
