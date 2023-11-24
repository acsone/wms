# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models import product_supplierinfo


class ProductSupplierinfo(product_supplierinfo.SupplierInfo):

    reminder_mailing_sent = fields.Boolean()
