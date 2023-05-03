# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.report.sale_report import SaleReport as SaleReportBase


class SaleReport(SaleReportBase):

    month = fields.Selection(
        [
            ("01", "January"),
            ("02", "February"),
            ("03", "March"),
            ("04", "April"),
            ("05", "May"),
            ("06", "June"),
            ("07", "July"),
            ("08", "August"),
            ("09", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        readonly=True,
    )

    def _select_sale(self):
        res = super()._select_sale()
        # Add month value on select request for the sale report
        # Sale report is a report based on SQL request.
        return res + ", TO_CHAR(s.date_order, 'MM') as month"
