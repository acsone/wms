# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.addons.product.models.product_category import (
    ProductCategory as ProductCategoryBase,
)


class ProductCategory(ProductCategoryBase):
    def has_for_parent(self, category):
        self.ensure_one()
        return self == category or category.id in self._get_parent_ids()

    def has_for_parent_xml_id(self, category_xml_id):
        return self.has_for_parent(self.env.ref(category_xml_id))

    def _get_parent_ids(self):
        self.ensure_one()
        return [int(cat_id) for cat_id in self.parent_path.split("/") if cat_id]
