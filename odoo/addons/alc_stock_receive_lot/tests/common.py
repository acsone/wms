# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


class PackOperationLotAddCommon:
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.category_model = cls.env["product.category"]
        cls.product_model = cls.env["product.product"]
        cls.partner_model = cls.env["res.partner"]
        cls.lot_obj = cls.env["stock.lot"]

        # force parent_left/right computation
        cls.location_model = cls.env["stock.location"]
        # cls.location_model.pool._init = False

        cls.stock_picking_model = cls.env["stock.picking"]
        cls.stock_reception_wizard = cls.env["stock.pack.operation.lot.add"]

        barcodes = ["1234567", "123453"]

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.reception_location = cls.location_model.create(
            {
                "name": "reception",
                "location_id": cls.stock_location.id,
                "usage": "view",
            }
        )

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
        cls.bin1 = cls.location_model.create(
            {
                "name": "bin1",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        cls.bin2 = cls.location_model.create(
            {
                "name": "bin2",
                "location_id": cls.reception_location.id,
                "usage": "internal",
            }
        )
        picking_type = cls.env.ref("stock.picking_type_in")

        moves = cls.env["stock.move"].create(
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
        picking = cls.stock_picking_model.create(
            {
                "picking_type_id": picking_type.id,
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.reception_location.id,
                "move_ids": moves.ids,
                "move_line_ids": moves.mapped("move_line_ids").ids,
            }
        )
        picking = picking.with_context(test_mode=1)
        picking.action_assign()
        cls.picking = picking

    @classmethod
    def _create_lot(cls):
        product = cls.products.filtered(lambda p: p.name == "Unittest Reception P1")
        food_category = cls.env.ref("alc_product_food.product_categ_ali")
        product.categ_id = food_category
        cls.created_lot = cls.lot_obj.create(
            {
                "name": "010130",
                "expiration_date": "2030-01-01 10:00:00",
                "product_id": product.id,
                "company_id": cls.env.company.id,
            }
        )
