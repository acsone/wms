# Copyright 2021 ACSONE SA/NV
# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import api, fields

from odoo.addons.stock_storage_type.models import product_template
from odoo.addons.stock_storage_type.models.stock_package_type import StockPackageType


class ProductTemplate(product_template.ProductTemplate):

    is_new = fields.Boolean(related="package_type_id.is_new", store=True)
    new_product_with_old_date = fields.Boolean(
        default=False,
        compute="_compute_new_product_with_old_date",
        search="_search_new_product_with_old_date",
    )

    package_type_id = fields.Many2one[StockPackageType](
        copy=False,
        default=lambda self: self.env.ref(
            "alc_product_is_new.package_st_M_M_Nouveaute"
        ),
    )

    def _get_new_products_older_than_a_month(self):
        current_ids = self._get_current_ids()
        self.env.cr.execute(
            """
            SELECT DISTINCT pt.id
                FROM
                        product_template pt
                JOIN stock_package_type spt
                    ON pt.package_type_id = spt.id
                WHERE
                        spt.is_new
                    AND pt.create_date < NOW() - '1 month'::interval
                %(ids)s
            """,
            {"ids": current_ids},
        )
        result = self.env.cr.fetchall()
        ids = [r[0] for r in result]
        return ids

    @api.depends("is_new")
    def _compute_new_product_with_old_date(self):
        ids_new_products_old_date = set(self._get_new_products_older_than_a_month())
        for product in self:
            product.new_product_with_old_date = product.id in ids_new_products_old_date

    def _search_new_product_with_old_date(self, operator, value):
        ids = self._get_new_products_older_than_a_month()
        return [("id", "in", ids)]

    def _get_current_ids(self):
        """
        Copied from alc_product_audit because detected as a missing hidden dependency.

        Taking alc_product_audit as dependency just for this method looks overkill
        """
        if self.ids and len(self.ids) > 1:
            current_ids = AsIs(f"AND pt.id in {tuple(self.ids)}")
        elif self.ids and len(self.ids) == 1:
            current_ids = AsIs(f"AND pt.id = {self.ids[0]}")
        else:
            current_ids = AsIs("")
        return current_ids
