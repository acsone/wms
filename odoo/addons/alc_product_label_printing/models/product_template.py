# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.product.models.product_template import ProductTemplate as Product


class ProductTemplate(Product):
    number_labels_to_print = fields.Integer(
        default=1,
        string="Number of Labels to Print.",
        help="This field determines how many Product/Customer labels to print, "
        "and only these labels. Set to 0 to skip printing any.",
    )
