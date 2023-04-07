from odoo.fields import Command
from odoo.tests import TransactionCase


class TestAverageSaleCommon(TransactionCase):
    @classmethod
    def _create_so(cls, product, quantity):
        so = cls.so.create(
            {
                "partner_id": cls.env.ref("base.res_partner_3").id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": quantity,
                        }
                    )
                ],
            }
        )
        so.action_confirm()
        return so

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_1 = cls.env["product.product"].create({"name": "TEST_1"})
        cls.product_2 = cls.env["product.product"].create({"name": "TEST_2"})
        cls.precision = cls.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        cls.so = cls.env["sale.order"]
