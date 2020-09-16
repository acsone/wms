# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class StockDeliveryNoteAdditionalProductTestCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(StockDeliveryNoteAdditionalProductTestCase, cls).setUpClass()
        cls.tax = cls.env["account.tax"].create(
            {
                "tax_group_id": cls.env.ref("specific_data.vat_tax_group").id,
                "amount": 6,
                "name": "test_tax",
            }
        )
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
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
        cls.warehouse_1.pick_type_id.subcode = "PICK"
        cls.warehouse_1.pick_type_id.groupbypartner = False
        cls.warehouse_1.out_type_id.groupbypartner = True
        cls.warehouse_1.out_type_id.create_invoice_on_transfer = True

        # Create additional product and update the available quantity (15)
        cls.additional_product = cls.env["product.product"].create(
            {
                "name": "Additional product",
                "default_code": "987654321",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.additional_product.id,
                "product_tmpl_id": cls.additional_product.product_tmpl_id.id,
                "new_quantity": 15,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )
        update_qty_wizard.change_product_qty()

        # Create main product linked to the additional product with quanity 20
        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Main product",
                "default_code": "1234567",
                "tracking": "none",
                "list_price": 100,
                "type": "product",
                "additional_product_id": cls.additional_product.id,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "ratio_main_product": 1,
                "ratio_additional_product": 1,
            }
        )

        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.main_product.id,
                "product_tmpl_id": cls.main_product.product_tmpl_id.id,
                "new_quantity": 100,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )
        update_qty_wizard.change_product_qty()

    @classmethod
    def _confirm_sale_order(cls, partner=None, product=None, qty=1, carrier_id=None):
        if partner is None:
            partner = cls.partner1
        if product is None:
            product = cls.main_product
        warehouse = cls.warehouse_1
        Sale = cls.env["sale.order"]
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
                        "product_uom_qty": 10,
                        "product_uom": cls.env.ref("product.product_uom_unit").id,
                        "price_unit": 50,
                        "tax_id": [(4, cls.tax.id, False)],
                    },
                )
            ],
        }
        if carrier_id:
            so_values["carrier_id"] = carrier_id
        so = Sale.create(so_values)
        so.action_confirm()
        return so

    @classmethod
    def create_pick(cls, sale):
        pick = sale.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        pick.with_context(round_autoset=False).action_assign()
        return pick
