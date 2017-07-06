# -*- coding: utf-8 -*-
from odoo import models, fields, _, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    operator_code = fields.Char('Operator ID')

    _sql_constraints = [
        (
            'unique_operator_code',
            'unique(operator_code)',
            _('The operator ID should be unique.')
        ),
    ]

    @api.model
    def get_user(self, operator_code):
        return self.sudo().search([('operator_code', '=', operator_code)])
