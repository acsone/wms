# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestActAsView(TransactionCase):
    @classmethod
    def setUpClass(cls):
        res = super().setUpClass()
        cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product test 1",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Test Code stock lot update",
                "tracking": "lot",
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product test 2",
                "type": "product",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
                "default_code": "Test Code stock lot update",
                "tracking": "lot",
            }
        )
        cls.lot_1 = cls.env["stock.lot"].create(
            {
                "name": "test_stock_lot_update 1",
                "product_id": cls.product_1.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )

        cls.lot_2 = cls.env["stock.lot"].create(
            {
                "name": "test_stock_lot_update 2",
                "product_id": cls.product_2.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )

        cls.quant_1 = cls.env["stock.quant"].create(
            {
                "product_id": cls.product_1.id,
                "location_id": cls.env.ref("stock.stock_location_14").id,
                "quantity": 50,
                "lot_id": cls.lot_1.id,
            }
        )

        cls.quant_2 = cls.env["stock.quant"].create(
            {
                "product_id": cls.product_1.id,
                "location_id": cls.env.ref("stock.stock_location_14").id,
                "quantity": 50,
                "lot_id": cls.lot_2.id,
            }
        )
        return res

    def test_wizard(self):
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.ref("stock.picking_type_out"),
                "location_dest_id": self.ref("stock.stock_location_output"),
                "location_id": self.ref("stock.stock_location_company"),
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": self.product_1.name,
                "product_id": self.product_1.id,
                "product_uom_qty": 50,
                "product_uom": self.product_1.uom_id.id,
                "picking_id": picking.id,
                "location_dest_id": picking.location_dest_id.id,
                "location_id": picking.location_id.id,
                "lot_ids": [self.lot_1.id],
            }
        )

        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": self.product_1.id,
                "lot_id": self.lot_1.id,
            }
        )
        wizard = (
            self.env["stock.lot.update"].with_context(active_id=self.lot_1.id).new()
        )

        # We first update the product when the move has only one lot, which should work
        wizard.product_id = self.product_2.id
        wizard.action_update()

        # We then add a second lot to the move and update the product on lot 1.
        # This cannot happen because one move cannot have lots with different products.
        self.env["stock.move.line"].create(
            {
                "move_id": move.id,
                "product_id": self.product_2.id,
                "lot_id": self.lot_2.id,
            }
        )
        wizard.product_id = self.product_1
        with self.assertRaises(ValidationError), self.cr.savepoint():
            wizard.action_update()
