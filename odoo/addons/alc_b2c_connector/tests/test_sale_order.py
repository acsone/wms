# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tools.misc import mute_logger

from .common import CommonB2CServiceCase


class TestSaleOrder(CommonB2CServiceCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create a b2c_partner
        cls.partner = cls.env["res.partner"].create({"name": "test partner"})

        cls.b2c_order = cls.env["sale.order"].create(
            {
                "b2c_ref": 10,
                "sale_channel_id": cls.sale_channel.id,
                "partner_id": cls.partner.id,
            }
        )

    def test_00(self):
        """
        Test Case:

            Create a new SO with the same b2c_ref and channel as the existing
            one
        Expected Result:
            IntegrityError
        """
        with self.assertRaises(IntegrityError), mute_logger("odoo.sql_db"):
            self.env["sale.order"].create(
                {
                    "b2c_ref": 10,
                    "sale_channel_id": self.sale_channel.id,
                    "partner_id": self.partner.id,
                }
            )

    def test_01(self):
        """
        Test Case:

            Create a new SO with the same b2c_ref and a different channel
            as the existing one
        Expected Result:
            A new order is created
        """
        self.assertTrue(
            self.env["sale.order"].create(
                {
                    "b2c_ref": 10,
                    "sale_channel_id": self.sale_channel2.id,
                    "partner_id": self.partner.id,
                }
            )
        )

    @mute_logger("odoo.addons.alc_b2c_connector.models.sale_order")
    def test_check_internal_sale_channel(self):
        """Regular users can't use external sale channels for not b2c orders."""
        self.sale_channel.is_internal = False
        with self.assertRaises(ValidationError):
            self.env["sale.order"].with_user(self.env.ref("base.user_demo")).create(
                {
                    "sale_channel_id": self.sale_channel.id,
                    "partner_id": self.partner.id,
                }
            )

        self.env["sale.order"].with_user(self.env.ref("base.user_demo")).create(
            {
                "b2c_ref": 20,
                "sale_channel_id": self.sale_channel.id,
                "partner_id": self.partner.id,
            }
        )

        self.sale_channel.is_internal = True
        self.env["sale.order"].with_user(self.env.ref("base.user_demo")).create(
            {
                "sale_channel_id": self.sale_channel.id,
                "partner_id": self.partner.id,
            }
        )

        self.env["sale.order"].create(
            {
                "sale_channel_id": self.sale_channel.id,
                "partner_id": self.partner.id,
            }
        )
