# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class ProductSupplierinfoEsbflux(models.Model):
    """Keep track of the actions to add in xml

    Two esb flux based on product.supplierinfo have an action tag in them, to
    send udpates of the promotions. Possible actions are delete and create.
    So on creation and updates of a promotions this model is updated so the
    flux can be properly generated later on
    """
    _name = 'product.supplierinfo.esbflux'
    _description = 'ESB Promotions XML'

    action = fields.Selection(
        string='Action',
        selection=[('delete', 'Delete'),
                   ('create', 'Create')]
    )
    flux = fields.Selection(
        string='Flux name',
        selection=[('buyxgety', 'Buy X Get Y'),
                   ('specialpromotion', 'Special Promotion')],
    )
    real_id = fields.Integer(
        string='Real Id'
    )
    # Fields from table product.supplierinfo, needed for the mapping later
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template',
        index=True,
        ondelete='cascade',
    )
    ratio_main_product = fields.Integer('Ratio Main Product')
    ratio_promotional_product = fields.Integer('Ratio Free Product')
    discount_sale = fields.Float(
        'Sale discount (%)',
        digits=dp.get_precision('Discount'),
        default=0.0
    )
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')

    @api.multi
    def remove_duplicate_actions(self):
        """Delete duplicate action in a flux ready to be send

        When a group of action is sent repetitive Create/Delete are unnecessary
        so here we purge them.
        """

        def simplify_action(first, last):
            """Rules are the following

            start: Create   finish: Create  send: last Create
            start: Delete   finish: Delete  send: first Delete
            start: Create   finish: Delete  send: nothing
            start: Delete   finish: Create  send: both
            """
            if last is None:
                return first
            elif first.action == 'create' and last.action == 'create':
                return last
            elif first.action == 'delete' and last.action == 'delete':
                return first
            elif first.action == 'delete' and last.action == 'create':
                return self.browse() | first | last
            else:
                # Start with create and finish with delete, nothing to send
                return self.browse()

        if len(self) < 2:
            # A single record or nothing, leave it as is
            return self
        rs = self.sorted(key=lambda r: (r.real_id, r.id))
        new_rs = self.browse()
        first_action = None
        last_action = None
        for r in rs:
            if first_action is None:
                first_action = r
            elif first_action.real_id != r.real_id:
                new_rs |= simplify_action(first_action, last_action)
                first_action = r
                last_action = None
            else:
                last_action = r
        else:
            new_rs |= simplify_action(first_action, last_action)

        return new_rs
