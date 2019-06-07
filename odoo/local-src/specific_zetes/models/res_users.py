# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    operator_code = fields.Char('Operator ID')

    _sql_constraints = [
        (
            'unique_operator_code',
            'unique(operator_code)',
            _('The operator ID should be unique.'),
        )
    ]

    @api.model
    def get_user(self, operator_code):
        self_with_inactive = self.with_context(active_test=False)
        return self_with_inactive.search(
            [('operator_code', '=', operator_code)]
        )

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """ Search an user by his operator code (e: 02, 67, ...) """
        if not args:
            args = []

        result = super(ResUsers, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )

        if len(result) >= limit:
            return result

        limit_available = limit - len(result)
        existing_ids = [x[0] for x in result]
        # Execute a strict research (= and not ilike)
        users = self.search(
            [('operator_code', '=', name), ('id', 'not in', existing_ids)],
            limit=limit_available,
        )

        result += users.name_get()
        return result
