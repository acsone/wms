# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import datetime

from dateutil import relativedelta
from freezegun import freeze_time

from odoo import fields

from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import sale_statistics_router


class TestSaleStatistics(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = sale_statistics_router
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref("alc_product_food.product_categ_ali").id,
            }
        )
        cls.supplierpromotion = cls.env["product.supplierinfo"].create(
            {
                "partner_id": cls.supplier.id,
                "discount_sale": 10,
                "date_start": fields.Date.today(),
                "date_end": fields.Date.today(),
                "product_tmpl_id": cls.product_1.product_tmpl_id.id,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref(
                    "alc_product_category_data.product_categ_medoc"
                ).id,
            }
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner_2"})
        cls.partner_5y = cls.env["res.partner"].create({"name": "partner_5y"})
        for month, qties in [
            ("01", [5, 3]),
            ("02", [1, 3]),
            ("03", [5, 3, 1]),
            ("09", [1, 30]),
            ("12", [99, 1, 5, 8]),
        ]:
            for qty in qties:
                cls.sell(cls.product_1, qty, f"2020-{month}-01 00:00:00")

        # makes sales for top_ordered.... SQL view uses now() ->
        # created sales must be created from now....
        for month_offet, qties in [
            (1, [3]),
            (2, [7]),
            (4, [2]),
            (13, [567]),
        ]:
            for qty in qties:
                date_order = fields.Datetime.to_string(
                    datetime.now() - relativedelta.relativedelta(months=month_offet)
                )
                cls.sell(cls.product_2, qty, date_order)
                cls.sell(cls.product_1, qty / 2, date_order)
        cls.last_date_order = max(
            cls.env["sale.order"]
            .search(
                [
                    ("partner_id", "=", cls.partner_1.id),
                    ("state", "in", ["sale", "done"]),
                ]
            )
            .mapped("date_order")
        )
        cls.env.flush_all()
        cls.env["alc.eshop.product.ordered.qty"].refresh_view()

        # 5 years test
        year_now = datetime.now().year
        date_exp = "%s-12-12 00:00:00"
        cls.expected_5y = [
            {"food": 4, "equipment": 0, "meds": 0},
            {"food": 3, "equipment": 0, "meds": 0},
            {"food": 2, "equipment": 0, "meds": 0},
            {"food": 0, "equipment": 0, "meds": 0},
            {"food": 0, "equipment": 0, "meds": 14},
        ]
        p5y = cls.partner_5y
        # old data is fine
        cls.sell(cls.product_1, 7, date_exp % (year_now - 5), partner=p5y, invoice=True)
        cls.sell(cls.product_1, 4, date_exp % (year_now - 4), partner=p5y, invoice=True)
        cls.sell(cls.product_1, 3, date_exp % (year_now - 3), partner=p5y, invoice=True)
        cls.sell(cls.product_1, 2, date_exp % (year_now - 2), partner=p5y, invoice=True)
        cls.sell(cls.product_2, 14, date_exp % year_now, partner=p5y, invoice=True)
        # service resist to (bad) future data
        future_date = date_exp % (year_now + 1)
        cls.sell(cls.product_1, 21, future_date, partner=p5y, invoice=True)
        cls.env.flush_all()
        cls.env["alc.eshop.product.ordered.yearly"].refresh_view()

    @classmethod
    def sell(
        cls,
        product,
        qty,
        ttime,
        confirm=True,
        deliver=False,
        partner=False,
        invoice=False,
    ):
        partner = partner or cls.partner_1
        qty = int(qty)
        with freeze_time(ttime):
            so = cls.env["sale.order"].create(
                {
                    "partner_id": partner.id,
                    "sale_channel_id": cls.env.ref(
                        "alc_sale_channel.sale_channel_web"
                    ).id,
                    "date_order": ttime,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom": product.uom_id.id,
                                "product_uom_qty": qty,
                            },
                        )
                    ],
                }
            )
            if confirm or deliver or invoice:
                so.action_confirm()
            if deliver or invoice:
                so.picking_ids.action_confirm()
                so.picking_ids._action_done()
            if invoice:
                so._create_invoices()
                # temp fix account_cutoff_pincking
                # invoice lines linked to a "draft" move are no more
                # considered as invoiced... This breaks the test and normal
                # odoo behavior
                if "account.cutoff.line.invoice" in cls.env:
                    so.order_line.invoice_lines.move_id.action_post()
        return so
