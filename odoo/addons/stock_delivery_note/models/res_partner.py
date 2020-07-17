# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    send_csv_deliveryship = fields.Boolean(
        string="Send the deliveryship in CSV format", default=True
    )
    send_pdf_deliveryship = fields.Boolean(
        string="Send the deliveryship in PDF format", default=False
    )
