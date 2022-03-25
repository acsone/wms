# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    last_suite_name = fields.Char(
        string="Last Suite Name", compute="_compute_last_suite_name"
    )

    def _compute_last_suite_name(self):
        """ Compute the last suite name used for this customer.

        We take the suite name from his sale orders
        Used to be returned by WSO2
        """
        for record in self:
            order = self.env["sale.order"].search(
                [("partner_id", "=", record.id), ("suite_name", "!=", False)],
                order="date_order desc, id desc",
                limit=1,
            )
            if order:
                record.last_suite_name = order.suite_name
