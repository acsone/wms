# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, _


class ProductTemplateAdditional(models.Model):
    _name = 'product.template.additional'

    _sql_constraints = [
        (
            'original_quantity_positive',
            'CHECK(original_quantity > 0)',
            _('The original quantity must be positive.')
        ),
        (
            'quantity_positive',
            'CHECK(quantity > 0)',
            _('The quantity must be positive.')
        ),
    ]

    original_product_id = fields.Many2one(
        comodel_name='product.template',
        string='Original product',
        required=True,
        ondelete='cascade',
        index=True
    )
    original_quantity = fields.Integer(
        string='Original quantity',
        required=True
    )

    product_id = fields.Many2one(
        comodel_name='product.template',
        string='Additional product',
        ondelete='restrict',
        required=True
    )
    quantity = fields.Integer(
        string='Quantity',
        required=True
    )
    calculation_method = fields.Selection(
        selection=[
            ('once', 'Once'),
            ('proportional', 'Proportional'),
        ],
        string='Calculation method',
        default='once',
        required=True
    )
    is_free = fields.Boolean(
        string='Is free',
        required=True
    )
    position_on_sale = fields.Selection(
        selection=[
            ('just_after', 'Just after'),
            ('at_end', 'At end'),
        ],
        string='Position on sale',
        default='just_after',
        required=True
    )
