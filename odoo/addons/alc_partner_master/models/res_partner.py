# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):
    master_partner_id = fields.Many2one[BasePartner](string="Customer master")
