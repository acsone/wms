# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api


class ZelaproConfigSettings(models.TransientModel):
    _name = 'zelapro.config.settings'
    _inherit = 'res.config.settings'

    delimiter = fields.Char('Delimiter', required=True, default=';')
    export_path = fields.Char('Export path', required=True)
    turnover_delay = fields.Integer(
        'CA computation delay (in months)',
        required=True
    )
    date_go_live = fields.Date('Date GO live', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(ZelaproConfigSettings, self).default_get(fields)

        config_param = self.env['ir.config_parameter']
        if not fields or 'delimiter' in fields:
            delimiter = config_param.get_param('zelapro.delimiter')
            res['delimiter'] = delimiter
        if not fields or 'export_path' in fields:
            export_path = config_param.get_param('zelapro.export_path')
            res['export_path'] = export_path
        if not fields or 'turnover_delay' in fields:
            turnover_delay = \
                int(config_param.get_param('zelapro.turnover_delay'))
            res['turnover_delay'] = turnover_delay
        if not fields or 'date_go_live' in fields:
            date_go_live = config_param.get_param('zelapro.date_go_live')
            res['date_go_live'] = date_go_live

        return res

    @api.multi
    def set_delimiter(self):
        self.ensure_one()

        self.env['ir.config_parameter']\
            .set_param('zelapro.delimiter', self.delimiter)

    @api.multi
    def set_export_path(self):
        self.ensure_one()

        self.env['ir.config_parameter']\
            .set_param('zelapro.export_path', self.export_path)

    @api.multi
    def set_turnover_delay(self):
        self.ensure_one()

        self.env['ir.config_parameter']\
            .set_param('zelapro.turnover_delay',
                       str(self.turnover_delay))

    @api.multi
    def recompute_all_business_unit_id(self):
        """
        Force Odoo to recompute the business unit on each product
        :return:
        """
        products = self.env['product.product'].search([])
        products.with_context(tracking_disable=True)\
            ._compute_business_unit_id()

    @api.multi
    def recompute_all_abc_code(self):
        """
        Update the Turnover and recompute the ABC code for all products
        """
        products = self.env['product.product'].search([])
        products.with_context(tracking_disable=True).update_abc_code()
