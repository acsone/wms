# coding: utf-8
import datetime

from freezegun import freeze_time
from odoo.tests.common import SavepointCase


class SaleProcurementMTSMTOTestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(SaleProcurementMTSMTOTestCase, cls).setUpClass()
        # no rules, not paths on route MTO
        route_mto = cls.env.ref("stock.route_warehouse0_mto")
        route_buy = cls.env.ref("purchase.route_warehouse0_buy")

        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest partner1", "ref": "12344566777878"}
        )
        cls.seller = cls.env["res.partner"].create(
            {
                "name": "Unittest supplier",
                "ref": "1234456677780",
                "supplier": 1,
                "is_manage_day_5": True,
            }
        )
        cls.p1_mts = cls.env["product.product"].create(
            {
                "name": "Unittest P1 MTS",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "route_ids": [(4, route_buy.id)],
                "seller_ids": [
                    (0, 0, {"name": cls.seller.id, "price": 10, "delay": 2})
                ],
                "orderpoint_min": 0,
                "orderpoint_max": 10,
            }
        )
        cls.p2_mto = cls.env["product.product"].create(
            {
                "name": "Unittest P2 MTO",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
                "route_ids": [(4, route_mto.id), (4, route_buy.id)],
                "seller_ids": [
                    (0, 0, {"name": cls.seller.id, "price": 11, "delay": 2})
                ],
            }
        )

        cls.warehouse = cls.env.ref("stock.warehouse0")

        cls.warehouse.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse.pick_type_id.subcode = "PICK"
        cls.warehouse.pick_type_id.groupbypartner = True
        cls.warehouse.out_type_id.groupbypartner = True
        # move the output location of the WH out of the view location of the WH
        cls.warehouse.wh_output_stock_loc_id.location_id = (
            cls.warehouse.view_location_id.location_id
        )
        cls.loc_reserve = cls.env["stock.location"].create(
            {
                "name": "Reserve",
                "location_id": cls.warehouse.view_location_id.id,
                "usage": "internal",
                "kind": "reserve",
            }
        )

        # change the location of the buy route.
        # this must be done after changing the warehouse otherwise the write() will reset it.
        for rule in route_buy.pull_ids:
            # the automatic orderpoints created in stock_orderpoint_product are
            # on the view location
            rule.location_id = rule.warehouse_id.view_location_id
        route_mto.pull_ids.write({"active": False})
        route_mto.push_ids.write({"active": False})

    def _confirm_sale_order(self, partner=None, product=None, qty=1):
        if partner is None:
            partner = self.partner1
        if product is None:
            product = self.p1_mts
        warehouse = self.warehouse
        Sale = self.env["sale.order"]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "product_uom": product.uom_id.id,
                    },
                )
            ],
        }
        so = Sale.create(so_values)
        so.action_confirm()
        return so

    def test_sale_product_mto(self):
        today = datetime.datetime(2019, 12, 2, 12)
        with freeze_time(today):
            self._confirm_sale_order(product=self.p2_mto)
        rfq = self.env["purchase.order"].search([("partner_id", "=", self.seller.id)])
        self.assertTrue(rfq, "Did not get an RFQ on %s (%d)" % (today, 0))
        self.assertEqual(rfq.date_planned, "2019-12-05 14:00:00")

    def test_sale_product_mto_existing_quote(self):
        # first sale order
        self.test_sale_product_mto()
        # second sale order
        today = datetime.datetime(2019, 12, 2, 13)
        with freeze_time(today):
            self._confirm_sale_order(product=self.p2_mto, qty=5)
        rfq = self.env["purchase.order"].search([("partner_id", "=", self.seller.id)])
        self.assertEqual(len(rfq), 1)
        po_lines = rfq.order_line.filtered(lambda rec: rec.product_id == self.p2_mto)
        qty = sum(po_lines.mapped("product_qty"))
        self.assertEqual(qty, 1 + 5)

    def test_sale_product_mts(self):
        today = datetime.datetime(2019, 12, 2, 12)
        with freeze_time(today):
            self._confirm_sale_order(product=self.p1_mts)
        rfq = self.env["purchase.order"].search([("partner_id", "=", self.seller.id)])
        self.assertFalse(rfq, "got an RFQ on %s (%d)" % (today, 0))
        for offset in (1, 2, 3, 4):
            date = today + datetime.timedelta(days=offset)
            self._run_reordering_rules(date)
            rfq = self.env["purchase.order"].search(
                [("partner_id", "=", self.seller.id)]
            )
            if offset < 4:
                self.assertFalse(rfq, "got an RFQ on %s (%d)" % (today, offset))
            else:
                self.assertTrue(rfq, "Did not get an RFQ on %s (%d)" % (date, offset))
                self.assertEqual(rfq.date_planned, "2019-12-10 14:00:00")

    def _run_reordering_rules(self, date):
        company_id = self.env.user.company_id.id
        with freeze_time(date):
            Wiz = self.env["procurement.orderpoint.compute"].with_context(
                default_type="by_days"
            )
            values = Wiz.default_get(
                [
                    "type",
                    "is_manage_day_1",
                    "is_manage_day_2",
                    "is_manage_day_3",
                    "is_manage_day_4",
                    "is_manage_day_5",
                    "is_manage_day_6",
                    "is_manage_day_7",
                ]
            )
            # can't call procure_calculation because this delegates the
            # computation to a thread, so it won't be synchronous.  can't
            # really use _specific_procure_calculation_orderpoint because it
            # creates a new cursor, so emulate what is done here...
            context = self.env.context.copy()
            context.update(values)
            Proc = self.env["procurement.order"].with_context(context)
            Proc._procure_orderpoint_confirm(
                use_new_cursor=False, company_id=company_id
            )
