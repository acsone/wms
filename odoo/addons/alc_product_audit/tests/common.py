# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests.common import TransactionCase


class ProductCharacteristicsCommonFeatures(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.StockLocation = cls.env["stock.location"]
        cls.StockPicking = cls.env["stock.picking"]
        cls.ResPartner = cls.env["res.partner"]
        cls.partner = cls.ResPartner.create({"name": "Test partner", "ref": "85789284"})
        cls.stock_location = cls.env.ref("stock.stock_location_stock")

        cls.route_buy = cls.env.ref("purchase_stock.route_warehouse0_buy")

        cls.route_medoc = cls.env.ref(
            "__setup__.stock_location_route_pick_medoc", raise_if_not_found=False
        )

        cls.route_aliment = cls.env.ref(
            "__setup__.stock_location_route_pick_ali", raise_if_not_found=False
        )

        cls.location_ali = cls.StockLocation.create(
            {
                "name": "Aliment",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )

        cls.location_medoc = cls.StockLocation.create(
            {
                "name": "Medicament",
                "usage": "internal",
                "location_id": cls.stock_location.id,
            }
        )
        cls.zone_ali = cls.StockLocation.create(
            {"name": "A", "location_id": cls.location_ali.id, "is_zone": True}
        )

        cls.zone_gustave = cls.StockLocation.create(
            {"name": "G", "location_id": cls.location_medoc.id, "is_zone": True}
        )

        cls.location_product = cls.StockLocation.create(
            {
                "name": "GD80B2",
                "location_kind": "bin",
                "location_id": cls.zone_gustave.id,
            }
        )

        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.route_mto.active = True

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "sale_ok": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
                "barcode": "XXX0001",
                "default_code": "12345",
            }
        )
        cls.product_template = cls.product.product_tmpl_id

        cls.product1 = cls.env["product.product"].create(
            {
                "name": "Product without packaging",
                "sale_ok": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
                "barcode": "XXX0003",
                "default_code": "678910",
            }
        )
        cls.product_template1 = cls.product1.product_tmpl_id

        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product new",
                "sale_ok": True,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
                "default_code": "678911",
            }
        )

        cls.warehouse = cls.env.ref("stock.warehouse0")

        picking_sequence = cls.warehouse.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")

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

        if not cls.route_aliment:
            cls.route_aliment = cls.env["stock.route"].create(
                {
                    "name": "Aliments",
                    "rule_ids": [
                        fields.Command.create(
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

        cls.route_new = cls.env.ref(
            "__setup__.stock_location_route_new", raise_if_not_found=False
        )

        if not cls.route_new:
            cls.route_new = cls.env["stock.route"].create({"name": "Nouveautes"})
            cls.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "stock_location_route_new",
                    "model": "stock.route",
                    "res_id": cls.route_new.id,
                }
            )

        cls.location_mto = cls.env.ref(
            "__setup__.stock_location_onorder", raise_if_not_found=False
        )

        if not cls.location_mto:
            cls.location_mto = cls.StockLocation.create({"name": "Achetés-Vendus"})
            cls.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "stock_location_onorder",
                    "model": "stock.location",
                    "res_id": cls.location_mto.id,
                }
            )
            cls.zone_mto_aliment = cls.StockLocation.create(
                {"name": "A", "location_id": cls.location_mto.id, "is_zone": True}
            )

            cls.location_bin_mto = cls.StockLocation.create(
                {
                    "name": "AZ01A1",
                    "usage": "internal",
                    "location_id": cls.zone_mto_aliment.id,
                }
            )
            cls.stock_quant = cls.env["stock.quant"].create(
                {
                    "product_id": cls.product1.id,
                    "location_id": cls.location_bin_mto.id,
                    "quantity": 10,
                }
            )

        cls.categ_ali = cls.env.ref("alc_product_food.product_categ_ali")
        cls.categ_ali.route_ids = [(4, cls.route_aliment.id)]
        if not cls.route_medoc:
            cls.route_medoc = cls.env["stock.route"].create(
                {
                    "name": "Medicament",
                    "rule_ids": [
                        fields.Command.create(
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
        cls.categ_medoc = cls.env.ref("alc_product_category_data.product_categ_medoc")
        cls.categ_medoc.route_ids = [(4, cls.route_medoc.id)]

        cls.group = cls.env["procurement.group"].create({"name": "test"})

        cls.ProductPackaging = cls.env["product.packaging"]
        cls.product_palette = cls.ProductPackaging.create(
            {
                "name": "Palette",
                "qty": 80,
                "product_id": cls.product.id,
            }
        )
        cls.product_box = cls.ProductPackaging.create(
            {
                "name": "Box",
                "qty": 20,
                "product_id": cls.product.id,
            }
        )

        cls.location_mto._parent_store_compute()

        cls.po = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_planned": fields.Datetime.now(),
                "order_line": [
                    fields.Command.create(
                        {
                            "name": cls.product1.name,
                            "product_id": cls.product1.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_qty": 5,
                            "price_unit": 5,
                            "date_planned": fields.Datetime.now(),
                        },
                    ),
                ],
            }
        )
        cls.po.button_confirm()
        if "is_web" in cls.env["product.category"]._fields:
            cls.category = cls.env.ref("alc_product_shop_category.master")
            cls.env["product.template"].search([]).categ_ids |= cls.category
