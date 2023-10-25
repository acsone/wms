# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import AccessError
from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestAlcStockSecurityMaterial(TransactionCase):
    """
    This will test that Material users will have acces to only.

    their products (in Material Category).

    They should not have product manager access rights.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.category = cls.env.ref("alc_product_category_data.product_categ_materiel")
        cls.group_material = cls.env.ref("alc_stock_security.group_materials_manager")
        cls.material_user = cls.env["res.users"].create(
            {
                "name": "Material User",
                "login": "material",
                "groups_id": [Command.set(cls.group_material.ids)],
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Material",
                "categ_id": cls.category.id,
            }
        )

    def test_access(self):
        self.product.with_user(self.material_user).write({"name": "Test"})

    def test_no_access(self):
        self.material_user.groups_id -= self.group_material
        with self.assertRaises(AccessError):
            self.product.with_user(self.material_user).write({"name": "Test"})
