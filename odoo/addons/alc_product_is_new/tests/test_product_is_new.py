# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tests.common import TransactionCase


class TestProductIsNew(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        package_type_new = cls.env["stock.package.type"].create(
            {"name": "any name", "is_new": True}
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product new",
                "sale_ok": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "default_code": "678911",
            }
        )
        cls.product_template2 = cls.product2.product_tmpl_id
        cls.product_template2.package_type_id = package_type_new.id

    def test_00(self):
        """Product is new."""
        self.assertTrue(self.product_template2.is_new)

    def test_01(self):
        """Product is not new."""
        package_type = self.env["stock.package.type"].create({"name": "any name"})
        self.product_template2.package_type_id = package_type.id
        self.assertFalse(self.product_template2.is_new)
