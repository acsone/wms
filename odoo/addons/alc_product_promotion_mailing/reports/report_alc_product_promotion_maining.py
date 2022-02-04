# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class ParticularReport(models.AbstractModel):
    _name = "report.report_alc_product_promotion_mailing"

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env["report"]
        return report_obj.render(
            "alc_product_promotion_mailing.report_alc_product_promotion_mailing", data,
        )
