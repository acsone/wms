# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import fields

from odoo.addons.alc_pricelist_role_name.models import product_pricelist


class ProductPricelist(product_pricelist.ProductPricelist):

    old_role_name = fields.Char(string="Old Role Name", readonly=True)
    old_discount_role_name = fields.Char(string="Old Discount Role Name", readonly=True)
