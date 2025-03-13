# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import xml.etree.ElementTree as ET
from datetime import date, timedelta

from freezegun import freeze_time

from odoo import Command
from odoo.osv.expression import AND
from odoo.tests import Form
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.tests.common import BaseCommon


class TestStockMoveReportCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = date.today()
        cls.partner = cls.env["res.partner"].create(
            [
                {"name": "smr partner 1", "zip": "4020"},
                {"name": "smr partner 2", "zip": "6040"},
                {"name": "smr partner 3", "zip": "6840"},
            ]
        )
        cls.supplier = cls.env["res.partner"].create(
            [
                {"name": "smr supplier 1", "ask_sale_statistics": True},
                {"name": "smr supplier 2", "ask_sale_statistics": True},
            ]
        )

        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.delivery_steps = "pick_ship"
        # set sequence_code of Returns
        cls.warehouse.return_type_id.sequence_code = "test/IN"
        cls.loc_stock = cls.warehouse.lot_stock_id
        cls.product = cls.env["product.product"].create(
            [
                {"name": "smr product 1", "type": "product"},
                {"name": "smr product 2", "type": "product"},
                {"name": "smr product 3", "type": "product"},
            ]
        )
        cls.supplierinfo = cls.env["product.supplierinfo"].create(
            [
                {
                    "partner_id": cls.supplier[0].id,
                    "product_tmpl_id": cls.product[0].product_tmpl_id.id,
                },
                {
                    "partner_id": cls.supplier[0].id,
                    "product_tmpl_id": cls.product[2].product_tmpl_id.id,
                },
                {
                    "partner_id": cls.supplier[1].id,
                    "product_tmpl_id": cls.product[1].product_tmpl_id.id,
                },
            ]
        )
        cls.so = cls.env["sale.order"]
        today = date.today()
        for idx in range(3):
            with freeze_time(today - timedelta(days=idx + 1)):
                cls.env["stock.quant"]._update_available_quantity(
                    cls.product[idx], cls.loc_stock, 10
                )
                so = cls.env["sale.order"].create(
                    [
                        {
                            "partner_id": cls.partner[idx].id,
                            "warehouse_id": cls.warehouse.id,
                            "order_line": [
                                Command.create(
                                    {
                                        "name": cls.product[idx].name,
                                        "product_id": cls.product[idx].id,
                                        "product_uom_qty": 5 + idx,
                                        "product_uom": cls.product[idx].uom_id.id,
                                        "price_unit": 1,
                                    },
                                )
                            ],
                        },
                    ]
                )
                so.action_confirm()
                so.action_done()
                cls.so |= so
                pick_int = so.picking_ids.filtered(
                    lambda p: p.picking_type_id.code == "internal"
                )
                pick_out = so.picking_ids.filtered(
                    lambda p: p.picking_type_id.code == "outgoing"
                )
                cls._do_transfer(pick_int)
                cls._do_transfer(pick_out)
        ship = cls.so[0].order_line.move_ids.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )[0]
        cls._create_return(ship)

    @classmethod
    def _do_transfer(cls, pick):
        pick.action_set_quantities_to_reservation()
        pick._action_done()

    @classmethod
    def _create_return(cls, ship):
        stock_return_picking_form = Form(
            cls.env["stock.return.picking"].with_context(
                active_ids=ship.picking_id.ids,
                active_id=ship.picking_id.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = 2
        return_pick = stock_return_picking.create_returns()
        if isinstance(return_pick, dict):
            return_pick = cls.env["stock.picking"].browse(return_pick["res_id"])
        return_pick.move_ids.quantity_done = 2
        return_pick._action_done()

    def _get_stock_move_report_lines(self, date_start, date_end):
        wiz = self.env["alc.stock.move.report.wizard"].create(
            [{"date_start": date_start, "date_end": date_end}]
        )
        action = wiz.action_open_sale_statistics()
        filter_names = [
            x[15:] for x in action["context"] if x.startswith("search_default_")
        ]
        view = self.env["ir.ui.view"].browse(action["search_view_id"])
        root = ET.fromstring(view.arch_prev)
        domain = AND(
            [
                safe_eval(f.get("domain"), locals_dict={"context": action["context"]})
                for f in root.findall("filter")
                if f.get("name") in filter_names
            ]
        )
        return self.env["alc.stock.move.report"].search(domain)
