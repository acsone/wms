# -*- coding: utf-8 -*-
import importlib
from datetime import datetime

import mock
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.http import WebRequest, _request_stack
from odoo.tests.common import SavepointCase

from .. import constants
from ..tools.domain_interface import Parameters

DOMAIN = "http://localhost:8069/zetes/"
OPERATOR_CODE = "99"
DEFAULT_HEADER = [
    "208030824",
    "2.2.3",
    "3iV_101",
    "REQU_USERCONTEXT",
    OPERATOR_CODE,
    "1",
    "20170207",
    "072932",
    "98427733121320",
]
ROUND_CODE = 99
PARTNER_NAME = "Mr. Docteur Test"


# pylint: disable=missing-return
class ZetesTest(SavepointCase):
    post_install = True
    at_install = False

    def _default_header(self):
        return DEFAULT_HEADER

    @classmethod
    def tearDownClass(cls):
        _request_stack.pop()
        super(ZetesTest, cls).tearDownClass()

    @classmethod
    def setUpClass(cls):
        super(ZetesTest, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Simulate a Webrequest and push it on the stack so the
        # code will access to it when reading 'odoo.http.request'
        fake_request = WebRequest(mock.Mock(name="httprequest"))
        fake_request._cr = cls.env.cr
        fake_request._uid = cls.env.uid
        fake_request._context = cls.env.context
        fake_request.httprequest.args = {}
        _request_stack.push(fake_request)

        cls.env.user.write({"ref": "38229299884", "tz": "Europe/Brussels"})

        # Set all picking as finished (to not interfere with tests)
        query = "UPDATE stock_picking SET zetes_state = %s"
        cls.env.cr.execute(query, (constants.AS_FINISHED,))

        existing_user = cls.env["res.users"].search(
            [("operator_code", "=", OPERATOR_CODE)]
        )
        if existing_user:
            raise Exception(
                "An user already exist with the operator code %s."
                " We cannot execute tests without an user "
                "from scratch." % OPERATOR_CODE
            )

        cls.operator_user = cls.env["res.users"].create(
            {
                "name": "User test",
                "ref": "02984757889392",
                "login": "zetes_user_test",
                "operator_code": OPERATOR_CODE,
                "groups_id": [(4, cls.env.ref("stock.group_stock_user").id)],
                "tz": "Europe/Brussels",
                "lang": "en_US",
                "email": "hello@world.com",
            }
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": PARTNER_NAME,
                "ref": "93765921390",
                "is_sale_back_order_accepted": True,
            }
        )

        round_template = cls.env["round.template"].create(
            {
                "code": ROUND_CODE,
                "name": "Test",
                "time_leave_planned": 12.50,
                "time_picking_planned": 12.50,
            }
        )

        round_itinerary = cls.env["round.itinerary"].create(
            {
                "sequence": 100,
                "name": "Test itinerary",
                "code": "TEST1",
                "template_ids": [(6, 0, [round_template.id])],
                "partner_position_ids": [
                    (0, 0, {"sequence": 1, "partner_id": cls.partner.id})
                ],
            }
        )

        cls.round = cls.env["round.instance"].create(
            {
                "state": "draft",
                "template_id": round_template.id,
                "date": fields.Date.today(),
                "time_leave_planned": 12.50,
                "time_picking_planned": 12.50,
                "itinerary_ids": [(6, 0, [round_itinerary.id])],
            }
        )

        # There is a unique constraint on the zone code.
        # If you want to execute this test with an full DB, PostgreSQL will
        # raise an error.
        cls.picking_zone_medoc = cls.env.ref(
            "__setup__.picking_zone_medicament", raise_if_not_found=False
        )
        if not cls.picking_zone_medoc:
            cls.picking_zone_medoc = cls.env["picking.zone"].create(
                {"code": "01", "name": "Medicament"}
            )

        location_obj = cls.env["stock.location"]

        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.vlb_location = cls.stock_location.location_id

        fefo = cls.env.ref("product_expiry.removal_fefo").id
        cls.stock_location.removal_strategy_id = fefo

        cls.location_medoc = location_obj.create(
            {
                "name": "Medicament",
                "usage": "internal",
                "act_as_view": True,
                "location_id": cls.stock_location.id,
                "picking_zone_id": cls.picking_zone_medoc.id,
            }
        )

        cls.zone_gustave = location_obj.create(
            {"name": "G", "location_id": cls.location_medoc.id}
        )

        cls.product_categ_medoc = cls.env.ref("specific_data.product_categ_medoc")

        cls.location_product_1 = location_obj.create(
            {
                "name": "GD80B1",
                "kind": "bin",
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "B",
                "box": "1",
                "location_id": cls.zone_gustave.id,
                "bin_checksum_1": "12",
                "bin_checksum_2": "12",
            }
        )
        location_obj._parent_store_compute()

        # Product 1
        # Location: GD80B1
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Test medoc 1",
                "default_code": "1234567",
                "categ_id": cls.product_categ_medoc.id,
                "tracking": "lot",
                "list_price": 100,
                "indicated_price": 120,
                "type": "product",
                "stock_bin_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "location_id": cls.stock_location.id,
                            "bin_location_id": cls.location_product_1.id,
                        },
                    )
                ],
            }
        )

        one_year = datetime.now() + relativedelta(years=1)
        cls.lot_product_1 = cls.env["stock.production.lot"].create(
            {
                "name": "000000001",
                "product_id": cls.product_1.id,
                "removal_date": fields.Datetime.to_string(one_year),
            }
        )
        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.product_1.id,
                "product_tmpl_id": cls.product_1.product_tmpl_id.id,
                "new_quantity": 100,
                "lot_id": cls.lot_product_1.id,
                "location_id": cls.location_product_1.id,
            }
        )
        update_qty_wizard.change_product_qty()

        wh = cls.env.ref("stock.warehouse0")
        picking_sequence = wh.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")
        cls.picking_type_medoc = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Médicaments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "use_create_lots": False,
                "subcode": "PICK",
                "groupbypartner": True,
                "color": 7,
                "sequence": 4,
                "picking_zone_id": cls.picking_zone_medoc.id,
                "zetes_picking_type": constants.PICKING_ASSIGNMENT,
            }
        )

        tomorrow = fields.Datetime.to_string(datetime.now() + relativedelta(days=1))
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.picking_type_medoc.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": location_out.id,
                "min_date": tomorrow,
                "zetes_state": constants.AS_DEFAULT,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test medoc 1",
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 10,
                            "product_uom": cls.env.ref("product.product_uom_unit").id,
                            "picking_type_id": cls.picking_type_medoc.id,
                        },
                    )
                ],
            }
        )

        if not hasattr(cls, "disable_picking_validation"):
            cls.picking.action_assign()
        cls.round.button_close()

        cls.context = {}

    def format_result(self, result):
        """
        Convert a result (a string) to a Parameters object.
        This object will be use to handle values
        :param result:
        :return:
        """
        # Convert the string to a list
        result_formatted = result.split(",")

        # Remove first empty value (all result starts with a comma)
        result_formatted.pop(0)

        # Extract response values
        result_values = result_formatted[len(self._default_header()) :]

        # Retrieve the method (eg: RESP_USERCONTEXT)
        method = result_formatted[constants.METHOD_INDEX]
        action, domain = method.split("_")

        # Create an instance of the domain (eg: usercontext = > Usercontext)
        module_name = "openerp.addons.specific_zetes.tools.domain_{}".format(
            domain.lower()
        )
        module_obj = importlib.import_module(module_name)
        domain_cls = getattr(module_obj, domain.title())
        instance = domain_cls(
            self._default_header(), mock.MagicMock(name="Savepoint()")
        )

        # Create the instance of Parameter with the previous domain instance
        result_parameter = Parameters(instance, action=action, values=result_values)

        return result_parameter


class ZetesParkingTest(ZetesTest):
    def setUp(self):
        super(ZetesParkingTest, self).setUp()

        entree_location = self.env["stock.location"].create(
            {
                "name": "Entree",
                "usage": "internal",
                "act_as_view": True,
                "location_id": self.stock_location.id,
            }
        )

        parking_medoc_root = self.env["stock.location"].create(
            {
                "name": "Parking Medicaments",
                "usage": "internal",
                "act_as_view": True,
                "kind": "parking",
                "location_id": entree_location.id,
            }
        )

        # Create a parking T99 (GF80E3)
        self.parking_medoc = self.env["stock.location"].create(
            {
                "name": "T99",
                "kind": "parking",
                "usage": "internal",
                "location_id": parking_medoc_root.id,
                "picking_zone_id": self.picking_zone_medoc.id,
                "zone": "G",
                "corridor": "F",
                "shelf": "80",
                "height": "E",
                "box": "3",
                "bin_checksum_1": "12",
                "bin_checksum_2": "12",
            }
        )
        self.env["stock.location"]._parent_store_compute()

        # Set a quantity in this parking
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_1.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "new_quantity": 100,
                "location_id": self.parking_medoc.id,
                "lot_id": self.lot_product_1.id,
            }
        )
        update_qty_wizard.change_product_qty()

        wh = self.env.ref("stock.warehouse0")
        internal_sequence = wh.int_type_id.sequence_id
        self.picking_type_medoc = self.env["stock.picking.type"].create(
            {
                "name": "Rangement Medicaments",
                "code": "internal",
                "sequence_id": internal_sequence.id,
                "default_location_src_id": parking_medoc_root.id,
                "default_location_dest_id": self.location_medoc.id,
                "use_create_lots": False,
                "sequence": 9,
                "picking_zone_id": self.picking_zone_medoc.id,
                "zetes_picking_type": constants.RANGEMENT_ASSIGNMENT,
            }
        )

        self.parking_medoc.write(
            {"barcode_picking_type_id": self.picking_type_medoc.id}
        )


class ZetesReserveTest(ZetesTest):
    def setUp(self):
        super(ZetesReserveTest, self).setUp()

        reserve_medoc_root = self.env["stock.location"].create(
            {
                "name": "Reserve Medoc Root",
                "location_id": self.vlb_location.id,
                "usage": "internal",
                "act_as_view": True,
                "kind": "reserve",
            }
        )

        # Create the reserve RM99 (GD80X1)
        self.reserve_medoc = self.env["stock.location"].create(
            {
                "name": "RM99",
                "kind": "reserve",
                "usage": "internal",
                "location_id": reserve_medoc_root.id,
                "picking_zone_id": self.picking_zone_medoc.id,
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "X",
                "box": "1",
                "bin_checksum_1": "12",
                "bin_checksum_2": "12",
            }
        )
        self.env["stock.location"]._parent_store_compute()

        # Set a quantity in this reserve
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_1.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "new_quantity": 20,
                "location_id": self.reserve_medoc.id,
                "lot_id": self.lot_product_1.id,
            }
        )
        update_qty_wizard.change_product_qty()

        self.zone_gustave.write({"reserve_location_id": self.reserve_medoc.id})

        wh = self.env.ref("stock.warehouse0")
        internal_sequence = wh.int_type_id.sequence_id
        self.picking_type_medoc = self.env["stock.picking.type"].create(
            {
                "name": "Reassort Medicaments",
                "code": "internal",
                "sequence_id": internal_sequence.id,
                "default_location_src_id": reserve_medoc_root.id,
                "default_location_dest_id": self.location_medoc.id,
                "use_create_lots": False,
                "sequence": 9,
                "picking_zone_id": self.picking_zone_medoc.id,
                "zetes_picking_type": constants.REASSORT_ASSIGNMENT,
            }
        )

        self.reserve_medoc.write(
            {"barcode_picking_type_id": self.picking_type_medoc.id}
        )
