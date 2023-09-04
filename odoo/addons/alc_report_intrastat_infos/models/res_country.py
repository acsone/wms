# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.account_intrastat.models.res_country import ResCountry as Country


class ResCountry(Country):

    is_intrastat = fields.Boolean(string="Intrastat ready")
