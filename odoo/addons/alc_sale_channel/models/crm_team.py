# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.crm_team import CrmTeam as CrmTeamBase


class CrmTeam(CrmTeamBase):

    sale_channel_id = fields.Many2one(comodel_name="sale.channel")
