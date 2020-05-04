from .common import TestDeliveryRound


class TestRefillReport(TestDeliveryRound):
    @classmethod
    def setUpClass(cls):
        super(TestRefillReport, cls).setUpClass()
        cls.loc_bin = cls.env["stock.location"].create(
            {
                "name": "Bin",
                "location_id": cls.warehouse_1.lot_stock_id.id,
                "usage": "internal",
                "kind": "bin",
            }
        )
        cls.env["stock.location"]._parent_store_compute()
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )
        inventory = cls.env["stock.inventory"].create(
            {"name": "Test", "product_id": cls.p1.id, "filter": "product"}
        )
        inventory.prepare_inventory()
        # put 10 p3 in bin, and 100 in reserve
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p3.id,
                "product_uom_id": cls.p3.uom_id.id,
                "product_qty": 10,
                "location_id": cls.loc_bin.id,
            }
        )
        cls.env["stock.inventory.line"].create(
            {
                "inventory_id": inventory.id,
                "product_id": cls.p3.id,
                "product_uom_id": cls.p3.uom_id.id,
                "product_qty": 100,
                "location_id": cls.loc_reserve.id,
            }
        )
        inventory.action_done()

    def setup_alcyn2323(self):
        """
        Product p3 has:

        * qty 10 in bin location
        * qty 100 in "reserve" location

        Two orders for p3

        * SO1 : 6
        * SO2 : 50

        SO1 => delivery round 1 started, pick of 5 is done
        """
        # inventory is done in setUp
        self.delivery_round_1.button_resetdraft()
        # two sale orders for same product
        self.so1 = self._confirm_sale_order(self.partner1, product=self.p3, qty=6)
        self.so2 = self._confirm_sale_order(self.partner2, product=self.p3, qty=50)
        # so1 in round 1, which started
        self.delivery_round_1._assign_pickings(self.so1.picking_ids)
        # so1 picking done
        self.delivery_round_1.button_picking_start()
        preparation = self.so1.picking_ids.filtered(
            lambda p: p.picking_type_id == self.warehouse_1.pick_type_id
        )
        self.assertTrue(preparation.pack_operation_ids)
        pack_op = preparation.pack_operation_ids[0]
        pack_op.qty_done = 6.0
        wiz = self.env["stock.backorder.confirmation"].create(
            {"pick_id": preparation.id}
        )
        wiz._process()
        self.delivery_round_1.button_close()

        # second delivery round, open
        self.delivery_round_2 = self.env["round.instance"].create(
            {"template_id": self.delivery_template.id, "date": "2017-01-02"}
        )
        self.delivery_round_2.button_resetdraft()

    def test_alcyn2323_case1(self):
        """
        Case 1) SO2 => delivery round 2 does not exist, reassortment priority computed to 1000
        """
        self.setup_alcyn2323()
        prio_rec = self.env["report.stock.refill.reassort"].search(
            [("product_id", "=", self.p3.id)]
        )
        prio = prio_rec.refill_priority_reassort
        self.assertTrue(
            1000 <= prio < 2000,
            "reassort priority should be between 1000 and 2000 (actual: %d)" % prio,
        )

    def test_alcyn2323_case2(self):
        """
        Case 2) SO2 => delivery round 2 is not started, reassortment priority computed to 5000
        """
        self.setup_alcyn2323()
        self.delivery_round_2._assign_pickings(self.so2.picking_ids)
        prio_rec = self.env["report.stock.refill.reassort"].search(
            [("product_id", "=", self.p3.id)]
        )
        prio = prio_rec.refill_priority_reassort
        self.assertTrue(
            5000 <= prio < 6000,
            "reassort priority should be between 5000 and 6000 (actual: %d)" % prio,
        )

    def test_alcyn2323_case3(self):
        """
        Case 3) SO2 => delivery round 2 is started, reassortment priority computed to 6000
        """
        self.setup_alcyn2323()
        self.delivery_round_2._assign_pickings(self.so2.picking_ids)
        self.delivery_round_2.button_picking_start()
        prio_rec = self.env["report.stock.refill.reassort"].search(
            [("product_id", "=", self.p3.id)]
        )
        prio = prio_rec.refill_priority_reassort
        self.assertTrue(
            6000 <= prio, "reassort priority should be above 6000 (actual: %d)" % prio
        )
