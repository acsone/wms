# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.product.models.product_template import (
    ProductTemplate as ProductTemplateBase,
)


class ProductTemplate(ProductTemplateBase):
    def _compute_business_unit_property(self, field, cat_xmlid):
        for product in self:
            product[field] = product.categ_id.has_for_parent_xml_id(cat_xmlid)
