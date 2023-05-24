# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import TransactionCase

from odoo.addons.delivery_carrier_label_gls.tests.common import mock_gls_client

_mock_gls_client = mock_gls_client


class GLSCommonFeatures(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=True, NO_GLS_SEND=True)
        )
        cls.currency_id = cls.env.user.company_id.currency_id
        cls.carrier = cls.env.ref(
            "alc_delivery_carrier_gls.delivery_carrier_gls_be", raise_if_not_found=False
        )
        if not cls.carrier:

            cls.carrier = cls.env["delivery.carrier"].create(
                {
                    "name": "Unittest delivery GLS",
                    "delivery_type": "fixed",
                    "fixed_price": 10.0,
                }
            )
            cls.env["ir.model.data"].create(
                {
                    "module": "alc_delivery_carrier_gls",
                    "name": "delivery_carrier_gls_be",
                    "model": "delivery.carrier",
                    "res_id": cls.carrier.id,
                }
            )

        cls.carrier.write(
            {
                "price_rule_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "price_rule",
                            "variable": "price",
                            "operator": "<=",
                            "max_value": 300,
                        },
                    )
                ]
            }
        )
        vals_partner = {
            "name": "Unittest partner",
            "city": "Ramillies",
            "zip": "1367",
            "email": "rd@odoo.con",
            "street": "9, rue des bourlottes",
            "country_id": cls.env.ref("base.be").id,
            "ref": "12344566777878",
        }
        cls.partner1 = cls.env["res.partner"].create(vals_partner)
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Unittest P1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Unittest P2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
            }
        )
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "Unittest P3",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 30.0,
            }
        )

        cls.p4 = cls.env["product.product"].create(
            {
                "name": "Unittest P4",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 40.0,
            }
        )

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.code = "internal"

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.StockPicking = cls.env["stock.picking"]

        picking_sequence = cls.warehouse_1.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")

        cls.location_ali = cls.env["stock.location"].create(
            {
                "name": "Aliment",
                "usage": "view",
                "location_id": cls.stock_location.id,
            }
        )

        cls.location_medoc = cls.env["stock.location"].create(
            {
                "name": "Medicament",
                "usage": "view",
                "location_id": cls.stock_location.id,
            }
        )
        cls.zone_ali = cls.env["stock.location"].create(
            {"name": "A", "location_id": cls.location_ali.id}
        )

        cls.zone_medoc = cls.env["stock.location"].create(
            {"name": "G", "location_id": cls.location_medoc.id}
        )

        cls.location_product_medoc = cls.env["stock.location"].create(
            {"name": "GD80B2", "location_id": cls.zone_medoc.id}
        )

        cls.location_product_alim = cls.env["stock.location"].create(
            {"name": "AD80B2", "location_id": cls.zone_ali.id}
        )

        cls.env["stock.location"]._parent_store_compute()

        cls.picking_type_medoc = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Médicaments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "sequence_code": "PICK",
                "color": 7,
                "sequence": 4,
            }
        )

        cls.picking_type_ali = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Aliments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "sequence_code": "PICK",
                "color": 7,
                "sequence": 4,
            }
        )

        cls.route_aliment = cls.env["stock.route"].create(
            {
                "name": "Aliments",
                "rule_ids": [
                    Command.create(
                        {
                            "name": "pull_ali",
                            "location_dest_id": location_out.id,
                            "picking_type_id": cls.picking_type_ali.id,
                            "location_src_id": cls.location_ali.id,
                            "procure_method": "make_to_stock",
                            "action": "pull",
                        },
                    )
                ],
            }
        )

        cls.categ_ali = cls.env["product.category"].create({"name": "Alim category"})
        cls.categ_ali.route_ids = [(4, cls.route_aliment.id)]

        cls.route_medoc = cls.env.ref(
            "__setup__.stock_location_route_pick_medoc", raise_if_not_found=False
        )

        if not cls.route_medoc:
            cls.route_medoc = cls.env["stock.route"].create(
                {
                    "name": "Medicament",
                    "rule_ids": [
                        Command.create(
                            {
                                "name": "pull_medoc",
                                "location_dest_id": location_out.id,
                                "picking_type_id": cls.picking_type_medoc.id,
                                "location_src_id": cls.location_medoc.id,
                                "procure_method": "make_to_stock",
                                "action": "pull",
                            },
                        )
                    ],
                }
            )
            cls.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "stock_location_route_pick_medoc",
                    "model": "stock.location.route",
                    "res_id": cls.route_medoc.id,
                }
            )

        cls.categ_medoc = cls.env["product.category"].create(
            {"name": "Medeoc category"}
        )
        cls.categ_medoc.route_ids = [(4, cls.route_medoc.id)]

        # add p1 into medoc
        cls._set_qty_in_loc_only(cls.p1, 10, cls.location_product_medoc)
        cls.p1.categ_id = cls.categ_medoc
        cls.p1.route_ids = [(6, 0, cls.route_medoc.ids)]
        # add p2 into alim
        cls._set_qty_in_loc_only(cls.p2, 10, cls.location_product_alim)
        cls.p2.categ_id = cls.categ_ali
        cls.p2.route_ids = [(6, 0, cls.route_aliment.ids)]
        # add p3 into medoc
        cls._set_qty_in_loc_only(cls.p3, 10, cls.location_product_medoc)
        cls.p3.categ_id = cls.categ_medoc
        cls.p3.route_ids = [(6, 0, cls.route_medoc.ids)]
        # add p4 into alim
        cls._set_qty_in_loc_only(cls.p4, 10, cls.location_product_alim)
        cls.p4.categ_id = cls.categ_ali
        cls.p4.route_ids = [(6, 0, cls.route_aliment.ids)]

    @classmethod
    def _set_qty_in_loc_only(cls, product, qty, location=None):
        location = location or cls.env.ref("stock.stock_location_stock")
        inventory_quant = cls.env["stock.quant"].create(
            {
                "location_id": location.id,
                "product_id": product.id,
                "inventory_quantity": qty,
            }
        )
        inventory_quant.action_apply_inventory()

    @classmethod
    def _confirm_sale_order(
        cls, partner=None, product=None, qty=1, carrier_id=None, picking_policy="direct"
    ):
        if partner is None:
            partner = cls.partner1
        if product is None:
            product = cls.p1
        warehouse = cls.warehouse_1
        Sale = cls.env["sale.order"]
        lines = [
            (
                0,
                0,
                {
                    "name": p.name,
                    "product_id": p.id,
                    "product_uom_qty": qty,
                    "product_uom": p.uom_id.id,
                    "price_unit": 10,
                },
            )
            for p in product
        ]
        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": lines,
            "picking_policy": picking_policy,
        }
        if carrier_id:
            so_values["carrier_id"] = carrier_id
        so = Sale.create(so_values)
        so.action_confirm()
        return so
