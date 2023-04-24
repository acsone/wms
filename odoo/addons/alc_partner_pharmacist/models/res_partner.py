# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):

    pharmacist_id = fields.Many2one[BasePartner](string="Associated pharmacist")
    pharmacist_of_ids = fields.One2many[BasePartner](
        inverse_name="pharmacist_id",
        string="Pharmacist associated to",
    )
