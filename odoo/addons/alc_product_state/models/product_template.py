# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.product_state.models import product_template


class ProductTemplate(product_template.ProductTemplate):

    state_name = fields.Char(related="product_state_id.name", string="State name")
