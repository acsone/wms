# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    invoice_terms_conditions = fields.Text(
        related='company_id.invoice_terms_conditions',
        string='Invoice Terms and Conditions', translate=True
    )
    chunk_size = fields.Integer(
        'Nbr of partners by invoices creation job',
        default=lambda self:
        self.env['ir.config_parameter'].get_param('account.chunk_size', 0)
    )

    @api.multi
    def set_chunk_size(self):
        self.ensure_one()

        self.env['ir.config_parameter'] \
            .set_param('account.chunk_size', self.chunk_size)
