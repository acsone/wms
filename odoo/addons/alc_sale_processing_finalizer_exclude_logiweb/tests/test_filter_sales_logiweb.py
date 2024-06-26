# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestFilterSalesLogiweb(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "BWH",
            }
        )
        cls.SaleOrder = cls.env["sale.order"]
        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "12344566777874"}
        )
        cls.logiweb_partner = cls.env.ref("alc_logiweb.logiweb_partner")
        cls.logiweb_be_partner = cls.env.ref("alc_logiweb.logiweb_be_partner")
        cls.p1 = cls.env["product.product"].create(
            {"name": "Unittest P1", "type": "product"}
        )
        cls.p2 = cls.env["product.product"].create(
            {"name": "Unittest P2", "type": "product"}
        )
        cls.so_not_logiweb = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.p1.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.so_logiweb = cls.SaleOrder.create(
            {
                "partner_id": cls.logiweb_partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p2.name,
                            "product_id": cls.p2.id,
                            "product_uom_qty": 7,
                            "product_uom": cls.p2.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.so_logiweb_be = cls.SaleOrder.create(
            {
                "partner_id": cls.logiweb_be_partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p2.name,
                            "product_id": cls.p2.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.p2.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )

    def test_check_logiweb_lines_are_filtered_from_lines_to_cancel(self):
        all_lines = self.env["sale.order.line"].search([])
        all_partners = all_lines.mapped("order_id.partner_invoice_id")
        self.assertIn(self.logiweb_partner, all_partners)
        self.assertIn(self.logiweb_be_partner, all_partners)
        lines_to_cancel = self.env["sale.order"]._get_sales_bo_gt_3months_lines()
        to_cancel_partners = lines_to_cancel.mapped("order_id.partner_invoice_id")
        self.assertNotIn(self.logiweb_partner, to_cancel_partners)
        self.assertNotIn(self.logiweb_be_partner, to_cancel_partners)
