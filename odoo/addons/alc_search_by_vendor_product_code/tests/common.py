# Copyright 2024 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase


class TestMoveLineSearchCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.category_model = cls.env["product.category"]
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]
        cls.lot_obj = cls.env["stock.lot"]
        cls.location_model = cls.env["stock.location"]
        cls.stock_picking_model = cls.env["stock.picking"]
        barcodes = ["1234567", "123453"]
        cls.products = cls.product_model.create(
            [
                {
                    "name": "Unittest Reception P1",
                    "type": "product",
                    "uom_id": cls.env.ref("uom.product_uom_unit").id,
                    "tracking": "lot",
                    "barcode": barcodes[0],
                },
                {
                    "name": "Unittest Reception P2",
                    "type": "product",
                    "uom_id": cls.env.ref("uom.product_uom_unit").id,
                    "tracking": "lot",
                    "barcode": barcodes[1],
                },
            ]
        )
        warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.env.company.id)], limit=1
        )
        for product in cls.products:
            cls.env["stock.quant"].with_context(inventory_mode=True).create(
                {
                    "product_id": product.id,
                    "location_id": warehouse.lot_stock_id.id,
                    "inventory_quantity": 50,
                }
            )._apply_inventory()

        cls.supplier = cls.partner_model.create(
            {"name": "Unittest supplier", "ref": "839737475756467"}
        )

        cls.supplier_location = cls.location_model.browse(
            cls.env.ref("stock.stock_location_suppliers").id
        )
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.reception_location = cls.location_model.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "view",
            }
        )
        cls.env["stock.move"].create(
            [
                {
                    "location_id": cls.supplier_location.id,
                    "location_dest_id": cls.reception_location.id,
                    "name": "TEST MOVE RECEPTION ",
                    "product_id": product.id,
                    "product_uom": product.uom_id.id,
                    "product_uom_qty": 5.0,
                    "state": "waiting",
                }
                for product in cls.products
            ]
        )
        cls.product_code_base = "SUPPLIER_CODE"
        cls.product_code_1 = f"${cls.product_code_base}01"
        cls.product_code_2 = f"${cls.product_code_base}02"
        cls.product_1, cls.product_2 = cls.products
        cls.supplier_infos = cls.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": cls.supplier.id,
                    "price": 10,
                    "product_code": cls.product_code_1,
                    "product_tmpl_id": cls.product_1.product_tmpl_id.id,
                },
                {
                    "partner_id": cls.supplier.id,
                    "price": 10,
                    "product_code": cls.product_code_2,
                    "product_tmpl_id": cls.product_2.product_tmpl_id.id,
                },
            ]
        )
