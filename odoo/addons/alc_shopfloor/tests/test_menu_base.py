# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopfloor_base.tests.common_misc import MenuTestMixin

from .common import CommonCase


# pylint: disable=missing-return
class CommonMenuCase(CommonCase, MenuTestMixin):
    @classmethod
    def setUpClassVars(cls, *args, **kwargs):
        super(CommonMenuCase, cls).setUpClassVars(*args, **kwargs)
        ref = cls.env.ref
        profile1 = ref("shopfloor_base.profile_demo_1")
        cls.profile = profile1.sudo().copy()
        menu_xid_pref = "alc_shopfloor.shopfloor_menu_"
        cls.menu_items = ref(menu_xid_pref + "location_content_transfer")
        # Isolate menu items
        cls.menu_items.sudo().write({"profile_id": cls.profile.id})
        cls.env["shopfloor.menu"].search(
            [("id", "not in", cls.menu_items.ids)]
        ).sudo().write({"profile_id": profile1.id})

    def setUp(self):
        super(CommonMenuCase, self).setUp()
        with self.work_on_services(profile=self.profile) as work:
            self.service = work.component(usage="menu")

    def _data_for_menu_item(self, menu, **kw):
        data = super(CommonMenuCase, self)._data_for_menu_item(menu, **kw)
        expected_counters = kw.get("expected_counters") or {}
        data.update(
            {
                "picking_types": [
                    {"id": picking_type.id, "name": picking_type.name}
                    for picking_type in menu.picking_type_ids
                ],
            }
        )
        counters = expected_counters.get(
            menu.id,
            {
                "operations_count": 0,
                "picking_count": 0,
                "priority_operations_count": 0,
                "priority_picking_count": 0,
            },
        )
        data.update(counters)
        return data


# pylint: disable=missing-return
class MenuCountersCommonCase(CommonMenuCase):
    @classmethod
    def setUpClassVars(cls, *args, **kwargs):
        super(MenuCountersCommonCase, cls).setUpClassVars(*args, **kwargs)
        cls.menu1 = cls.env.ref(
            "alc_shopfloor.shopfloor_menu_location_content_transfer"
        )
        cls.menu1_picking_type = cls.menu1.picking_type_ids[0]

    @classmethod
    def setUpClassBaseData(cls, *args, **kwargs):
        super(MenuCountersCommonCase, cls).setUpClassBaseData(*args, **kwargs)
        cls.env["stock.location"]._parent_store_compute()
        cls.packing_location.sudo().active = True
        # We want to limit the tests to a dedicated location in Stock/ to not
        # be bothered with pickings brought by demo data
        cls.zone_location1 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "Zone location 1",
                    "location_id": cls.stock_location.id,
                    "barcode": "ZONE_LOCATION_1",
                }
            )
        )
        cls.zone_location2 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "Zone location 2",
                    "location_id": cls.stock_location.id,
                    "barcode": "ZONE_LOCATION_2",
                }
            )
        )
        # Set default location for our picking types
        cls.menu1_picking_type.sudo().default_location_src_id = cls.zone_location1
        cls.zone_sublocation1 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "Zone sub-location 1",
                    "location_id": cls.zone_location1.id,
                    "barcode": "ZONE_SUBLOCATION_1",
                }
            )
        )
        cls.zone_sublocation2 = (
            cls.env["stock.location"]
            .sudo()
            .create(
                {
                    "name": "Zone sub-location 2",
                    "location_id": cls.zone_location2.id,
                    "barcode": "ZONE_SUBLOCATION_2",
                }
            )
        )
        cls.product_e = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product E",
                    "type": "product",
                    "default_code": "E",
                    "barcode": "E",
                    "weight": 3,
                }
            )
        )
        cls.product_f = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product F",
                    "type": "product",
                    "default_code": "F",
                    "barcode": "F",
                    "weight": 3,
                }
            )
        )
        cls.product_g = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product G",
                    "type": "product",
                    "default_code": "G",
                    "barcode": "G",
                    "weight": 3,
                }
            )
        )
        cls.product_h = (
            cls.env["product.product"]
            .sudo()
            .create(
                {
                    "name": "Product H",
                    "type": "product",
                    "default_code": "H",
                    "barcode": "H",
                    "weight": 3,
                }
            )
        )
        # products = (
        #     cls.product_a
        #     + cls.product_b
        #     + cls.product_c
        #     + cls.product_d
        #     + cls.product_e
        #     + cls.product_f
        #     + cls.product_g
        #     + cls.product_h
        # )
        # for product in products:
        #    cls.env["stock.location.path"].sudo().create(
        #        {
        #            "product_id": product.id,
        #            "location_in_id": cls.stock_location.id,
        #            "location_out_id": cls.shelf1.id,
        #        }
        #    )

        cls.picking1 = picking1 = cls._create_picking(
            picking_type=cls.menu1_picking_type, lines=[(cls.product_a, 10)]
        )
        picking1.priority = "2"
        cls._fill_stock_for_moves(
            picking1.move_lines, in_package=True, location=cls.zone_sublocation1
        )

        cls.picking2 = picking2 = cls._create_picking(
            picking_type=cls.menu1_picking_type,
            lines=[(cls.product_b, 10), (cls.product_c, 10)],
        )
        picking2.priority = "3"
        cls._fill_stock_for_moves(
            picking2.move_lines, in_lot=True, location=cls.zone_sublocation2
        )

        cls.picking3 = picking3 = cls._create_picking(
            picking_type=cls.menu1_picking_type, lines=[(cls.product_d, 10)]
        )
        picking3.priority = "2"
        cls._fill_stock_for_moves(picking3.move_lines, location=cls.zone_sublocation1)

        cls.pickings = picking1 | picking2 | picking3
        cls.pickings.action_assign()
