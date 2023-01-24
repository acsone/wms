# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields

from odoo.addons.product.models.product_category import ProductCategory
from odoo.addons.product.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):

    business_unit_id = fields.Many2one[ProductCategory](
        string="Business unit",
        compute="_compute_business_unit_id",
        readonly=True,
        store=True,
    )

    @api.depends("categ_id", "categ_id.is_business_unit", "categ_id.parent_path")
    def _compute_business_unit_id(self):
        categ_ids = self.mapped("categ_id.id")
        if not categ_ids:
            self.write({"business_unit_id": False})
            return True
        sql = """
                SELECT
                    categ.id,
                    bu.id as business_unit_id
                FROM
                    product_category categ
                    JOIN product_category bu ON (
                        bu.is_business_unit = True
                        AND (
                            categ.id = bu.id
                            OR categ.parent_path like bu.parent_path || %s
                        )
                    )
                WHERE
                    categ.id in %s
            """
        self.env.cr.execute(sql, ["%", tuple(categ_ids)])
        bu_id_by_categ_id = dict(self.env.cr.fetchall())
        for product in self:
            product.business_unit_id = bu_id_by_categ_id.get(product.categ_id.id)
        return True
