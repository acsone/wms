# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.account_analytic_account_tag.models.account_analytic_account import (
    AccountAnalyticAccount as AnalyticAccount,
)
from odoo.addons.account_analytic_tag.models.account_analytic_tag import (
    AccountAnalyticTag,
)


class AccountAnalyticAccount(AnalyticAccount):
    _inherit = "account.analytic.account"

    tag_1_id = fields.Many2one[AccountAnalyticTag](
        string="Tag 1",
        compute="_compute_tag_id",
        store=True,
        index=True,
    )
    tag_2_id = fields.Many2one[AccountAnalyticTag](
        string="Tag 2",
        compute="_compute_tag_id",
        store=True,
        index=True,
    )
    tag_3_id = fields.Many2one[AccountAnalyticTag](
        string="Tag 3",
        compute="_compute_tag_id",
        store=True,
        index=True,
    )

    @api.depends("tag_ids")
    def _compute_tag_id(self):
        for rec in self:
            tags_by_color = {t.color: t for t in rec.tag_ids}
            rec.tag_1_id = tags_by_color.get(1, False)
            rec.tag_2_id = tags_by_color.get(2, False)
            rec.tag_3_id = tags_by_color.get(3, False)
