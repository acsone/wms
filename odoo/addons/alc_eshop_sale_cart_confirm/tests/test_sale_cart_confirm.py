# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from freezegun import freeze_time

from odoo.exceptions import ValidationError

from odoo.addons.alc_eshop_sale_cart_info.tests.common import (
    TestSaleCartRestApiInfoCase,
)


class TestSaleCartRestApi(TestSaleCartRestApiInfoCase):
    @contextmanager
    def _record_new_note_template(self, so):
        class _Result:
            new_mails = self.env["mail.mail"].browse()

        template = self.env.ref("alc_eshop_sale_cart_confirm.sale_order_notify_note")
        domain = [
            (
                "subject",
                "=",
                template.render_template(template.subject, so._name, so.id),
            )
        ]
        template.auto_delete = False
        all_mails = self.env["mail.mail"].search(domain)
        result = _Result()
        yield result
        result.new_mails = self.env["mail.mail"].search(domain) - all_mails

    def test_confirm(self):
        date_order = "2020-01-01 20:00:00"
        self.so.date_order = date_order
        self.assertEqual(date_order, self.so.date_order)
        confirm_date = "2021-01-01 07:10:00"
        with freeze_time(confirm_date):
            info = self.cart.dispatch(
                "confirm",
                params={
                    "uuid": self.so.uuid,
                    "customer_ref": "my_ref",
                    "note": "my note",
                },
            )

        self.assertEqual("sale", self.so.state)
        self.assertEqual("my_ref", self.so.client_order_ref)
        self.assertEqual("my note", self.so.note)
        self.assertTrue(info)
        state = "processing" if "shopinvader.backend" in self.env else "sale"
        self.assertEqual(state, info["state"])
        self.assertEqual("my_ref", info["customer_ref"])
        self.assertEqual("my note", info["note"])
        self.assertEqual(confirm_date, self.so.date_order)

    def test_confirm_with_note_sent_mail(self):
        with self._record_new_note_template(self.so) as result:
            self.cart.dispatch(
                "confirm",
                params={
                    "uuid": self.so.uuid,
                    "customer_ref": "my_ref",
                    "note": "my note",
                },
            )
        new_mail = result.new_mails
        self.assertTrue(new_mail)
        self.assertEqual(self.so.id, new_mail.res_id)
        self.assertEqual(self.so._name, new_mail.model)

    def test_confirm_without_note_sent_mail(self):
        with self._record_new_note_template(self.so) as result:
            self.cart.dispatch(
                "confirm",
                params={"uuid": self.so.uuid, "customer_ref": "my_ref", "note": ""},
            )
        new_mail = result.new_mails
        self.assertFalse(new_mail)

    def test_confirm_not_allowed(self):
        self.so.partner_id.eshop_ordering_allowed = False
        with self.assertRaises(ValidationError):
            self.cart.dispatch(
                "confirm", params={"uuid": self.so.uuid},
            )
        self.so.partner_id.eshop_ordering_allowed = True
        self.cart.dispatch(
            "confirm", params={"uuid": self.so.uuid},
        )
