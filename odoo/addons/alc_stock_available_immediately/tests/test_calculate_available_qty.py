# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase


class TestCalcAvailableQty(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location_model = cls.env["stock.location"]
        cls.stock_location_model = cls.env["stock.location"]
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {"name": "Unittest partner", "ref": "4929752"}
        )
        # make some stock
        cls._define_product_qty(cls.stock_location, cls.p1, 10.0)

    @classmethod
    def _define_product_qty(cls, location, product, quantity):
        cls.env["stock.quant"]._update_available_quantity(product, location, quantity)

    def _create_move(self, from_loc, to_loc, date):
        product_qty = 5
        picking_out = self.env["stock.picking"].create(
            {
                "partner_id": self.env.ref("base.res_partner_2").id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": from_loc.id,
                "location_dest_id": to_loc.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": self.p1.name,
                "product_id": self.p1.product_variant_ids.id,
                "product_uom_qty": product_qty,
                "product_uom": self.p1.uom_id.id,
                "picking_id": picking_out.id,
                "location_id": from_loc.id,
                "location_dest_id": to_loc.id,
                "date": date,
            }
        )
        picking_out.action_confirm()

    def test_same_prio(self):
        self.p1 = self.p1.with_context(prio=0, date=datetime.now() + timedelta(days=1))

        self._create_move(self.stock_location, self.customer_location, datetime.now())
        self.p1.invalidate_recordset()
        self.assertEqual(self.p1.immediately_usable_qty, 5.0)

    def test_higher_prio(self):
        self.p1 = self.p1.with_context(prio=1, date=datetime.now() + timedelta(days=1))
        self._create_move(self.stock_location, self.customer_location, datetime.now())
        self.p1.invalidate_recordset()
        self.assertEqual(self.p1.immediately_usable_qty, 10.0)

    def test_same_prio_later_date(self):
        self.p1 = self.p1.with_context(prio=0, date=datetime.now())

        self._create_move(
            self.stock_location,
            self.customer_location,
            datetime.now() + timedelta(days=1),
        )
        self.p1.invalidate_recordset()
        self.assertEqual(self.p1.immediately_usable_qty, 10.0)
