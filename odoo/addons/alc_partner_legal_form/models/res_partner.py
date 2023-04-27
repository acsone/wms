# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as BasePartner

from .alc_partner_legal_form import AlcLegalForm


class ResPartner(BasePartner):

    legal_form_id = fields.Many2one[AlcLegalForm](string="Legal form")
