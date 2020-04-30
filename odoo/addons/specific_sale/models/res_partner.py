# -*- coding: utf-8 -*-
# © 2017 Julien Coux (Camptocamp)
# © 2018 Yannick Vaucher (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_suite_name = fields.Char(
        string='Last Suite Name', compute='_compute_last_suite_name'
    )
    help_with_fee = fields.Boolean(string='Helps with fees')
    auto_cancel_unavailable_qty_sold = fields.Boolean(
        string="Auto-cancel Unavailable Quantity",
        default=False,
        help=(
            "Automatically cancel unavailable ordered quantity to avoid the "
            "generation of backorders.\n"
            "In other words it will ship only immediately usable quantity."
        ),
    )

    def _compute_last_suite_name(self):
        """ Compute the last suite name used for this customer.

        We take the suite name from his sale orders
        Used to be returned by WSO2
        """
        for record in self:
            order = self.env['sale.order'].search(
                [('partner_id', '=', record.id), ('suite_name', '!=', False)],
                order='date_order desc, id desc',
                limit=1,
            )
            if order:
                record.last_suite_name = order.suite_name

    @api.multi
    def _compute_sale_lines_count(self):
        for partner in self:
            domain = [
                ('state', 'in', ['sale']),
                ('order_id.partner_id', '=', partner.id),
                ('product_qty_remains_to_deliver', '>', 0),
            ]

            partner.sale_lines_count = len(
                self.env['sale.order.line'].search(domain)
            )

    sale_lines_count = fields.Integer(compute='_compute_sale_lines_count')

    @api.multi
    def action_view_sale_lines_unavailable(self):
        self.ensure_one()

        action_data = self.env.ref(
            'specific_sale.action_sale_lines_unavailable_list'
        ).read()[0]
        action_data['domain'] = [
            ('state', 'in', ['sale']),
            ('order_id.partner_id', '=', self.id),
        ]

        return action_data
